"""CuloTon Telegram notifier.

Two modes:

  --mode deploy --sha <sha> --author <name> --message <text>
      Posts a "CuloTon update deployed" notice with commit link.
      Intended to run from the deploy workflow on non-bot commits.

  --mode news
      Picks the newest EN article that has not yet been announced,
      builds a multilingual digest (EN/RU/PL/DE title + summary +
      link to the article on culoton.fun) and posts it. Marks the
      article as announced in scripts/announced.db.

Both modes are graceful no-ops when TELEGRAM_BOT_TOKEN or
TELEGRAM_CHAT_ID environment variables are missing — so the
workflow can be merged before secrets are configured.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
DB_PATH = Path(__file__).resolve().parent / "announced.db"

LOCALES = ("en", "ru", "pl", "de")
FLAGS = {"en": "🇬🇧", "ru": "🇷🇺", "pl": "🇵🇱", "de": "🇩🇪"}
SITE = "https://culoton.fun"
GH_REPO_URL = "https://github.com/CuloTon/culoton"

TG_API_TIMEOUT = 20
TG_MAX_LEN = 4000  # Telegram limit is 4096 — keep margin for safety.


def tg_send(token: str, chat_id: str, text: str, *, disable_preview: bool = False) -> tuple[int, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true" if disable_preview else "false",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TG_API_TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    if not md_text.startswith("---"):
        return {}, md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}, md_text
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].lstrip("\n")


def db_init() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS announced (
            slug TEXT NOT NULL,
            kind TEXT NOT NULL,
            announced_at TEXT NOT NULL,
            PRIMARY KEY (slug, kind)
        )"""
    )
    conn.commit()
    return conn


def already_announced(conn: sqlite3.Connection, slug: str, kind: str) -> bool:
    cur = conn.execute("SELECT 1 FROM announced WHERE slug = ? AND kind = ?", (slug, kind))
    return cur.fetchone() is not None


def mark_announced(conn: sqlite3.Connection, slug: str, kind: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO announced (slug, kind, announced_at) VALUES (?, ?, ?)",
        (slug, kind, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def find_next_news(conn: sqlite3.Connection) -> tuple[str, dict] | None:
    en_dir = NEWS_DIR / "en"
    if not en_dir.exists():
        return None
    candidates: list[tuple[str, dict]] = []
    for path in en_dir.glob("*.md"):
        slug = path.stem
        if already_announced(conn, slug, "news"):
            continue
        try:
            fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  skip {path.name}: {e}", file=sys.stderr)
            continue
        if not fm.get("date") or not fm.get("title"):
            continue
        candidates.append((slug, fm))
    candidates.sort(key=lambda x: str(x[1].get("date", "")), reverse=True)
    return candidates[0] if candidates else None


def load_locale_meta(slug: str) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for loc in LOCALES:
        path = NEWS_DIR / loc / f"{slug}.md"
        if not path.exists():
            continue
        try:
            fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        title = (fm.get("title") or "").strip()
        summary = (fm.get("summary") or "").strip()
        if title and summary:
            out[loc] = (title, summary)
    return out


def deploy_notify(token: str, chat_id: str, *, sha: str, message: str, author: str) -> int:
    first_line = message.strip().splitlines()[0] if message.strip() else "(no message)"
    text = (
        f"🚀 <b>CuloTon update deployed</b>\n\n"
        f"{html.escape(first_line[:280])}\n\n"
        f"<b>By:</b> {html.escape(author)}\n"
        f"<b>Commit:</b> <a href=\"{GH_REPO_URL}/commit/{sha}\">{html.escape(sha[:7])}</a>\n"
        f"<b>Site:</b> {SITE}/"
    )
    status, body = tg_send(token, chat_id, text, disable_preview=True)
    if status != 200:
        print(f"deploy notify failed: status={status} body={body}", file=sys.stderr)
        return 1
    print(f"deploy notify sent: {sha[:7]}")
    return 0


def news_notify(token: str, chat_id: str) -> int:
    conn = db_init()
    found = find_next_news(conn)
    if not found:
        print("No new EN news to announce.")
        return 0
    slug, en_fm = found
    metas = load_locale_meta(slug)
    if "en" not in metas:
        print(f"Article {slug} missing EN metadata; skipping.")
        return 0

    parts: list[str] = ["🔥 <b>NEW ON CULOTON</b>", ""]
    for loc in LOCALES:
        if loc not in metas:
            continue
        title, summary = metas[loc]
        parts.append(f"{FLAGS[loc]} <b>{html.escape(title)}</b>")
        parts.append(f"<i>{html.escape(summary)}</i>")
        parts.append("")
    parts.append(f"→ <a href=\"{SITE}/news/{slug}\">Read on CuloTon</a>")
    text = "\n".join(parts)
    if len(text) > TG_MAX_LEN:
        text = text[: TG_MAX_LEN - 3] + "..."

    status, body = tg_send(token, chat_id, text)
    try:
        ok = json.loads(body).get("ok", False) if status == 200 else False
    except Exception:
        ok = False
    if not ok:
        print(f"news notify failed: status={status} body={body}", file=sys.stderr)
        return 1

    mark_announced(conn, slug, "news")
    print(f"Announced: {slug}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=("deploy", "news"))
    p.add_argument("--sha", default="")
    p.add_argument("--message", default="")
    p.add_argument("--author", default="")
    args = p.parse_args()

    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").lstrip("﻿").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing — skipping (no-op).")
        return 0

    if args.mode == "deploy":
        if not args.sha or not args.message or not args.author:
            print("deploy mode requires --sha --message --author", file=sys.stderr)
            return 2
        return deploy_notify(token, chat_id, sha=args.sha, message=args.message, author=args.author)
    return news_notify(token, chat_id)


if __name__ == "__main__":
    sys.exit(main())
