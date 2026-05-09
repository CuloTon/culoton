"""CuloTon Telegram notifier.

Three modes:

  --mode deploy --sha <sha> --author <name> --message <text>
      Posts a "CuloTon update deployed" notice with commit link.

  --mode news
      Picks the newest EN article that has not yet been announced,
      builds a multilingual digest (EN/RU/PL/DE title + summary +
      link to the article on culoton.fun) and posts it. Marks the
      article as announced in scripts/announced.db.

  --mode mcap
      Fetches $CULO market data from GeckoTerminal (price, FDV,
      24h change, 24h volume), builds a multilingual market-pulse
      message and posts it.

All modes are graceful no-ops when TELEGRAM_BOT_TOKEN or
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

from _culo_market import (  # noqa: E402
    CULO_CONTRACT,
    GECKO_NET,
    fetch_culo_data,
    fmt_change,
    fmt_money,
)

TG_API_TIMEOUT = 20
TG_MAX_LEN = 4000  # Telegram limit is 4096 — keep margin for safety.


def url_is_live(url: str, timeout: float = 5.0) -> bool:
    """HEAD-check the article URL before announcing. Guards against the
    race where update-and-deploy committed the file but FTP upload
    hasn't finished — without this we'd announce a 404 to the channel.
    """
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "culoton-bot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(f"url_is_live({url!r}) failed: {type(e).__name__}: {e}", file=sys.stderr)
        return False


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

    article_url = f"{SITE}/news/{slug}"
    if not url_is_live(article_url):
        print(f"Article URL not live yet: {article_url} — skipping; will retry next cron.")
        return 0

    parts: list[str] = ["🔥 <b>NEW ON CULOTON</b>", ""]
    for loc in LOCALES:
        if loc not in metas:
            continue
        title, summary = metas[loc]
        parts.append(f"{FLAGS[loc]} <b>{html.escape(title)}</b>")
        parts.append(f"<i>{html.escape(summary)}</i>")
        parts.append("")
    parts.append(f"→ <a href=\"{article_url}\">Read on CuloTon</a>")
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


# A few short FOMO lines per locale. We pick one at random each post so
# the message is not a copy-paste of itself every six hours. Lines are
# bullish but not cringe — confident, not begging.
FOMO_LINES = {
    "en": [
        "TON's quietly building, $CULO is along for the ride.",
        "Early-stage memecoin on the fastest chain in crypto. You know the drill.",
        "Small cap, big chain, attentive crew. Don't sleep on this one.",
        "While others chase noise, $CULO compounds on TON.",
        "The native token of CuloTon — and we're just getting started.",
    ],
    "ru": [
        "TON тихо строится, $CULO едет вместе с ним.",
        "Ранний мем-токен на одной из самых быстрых сетей. Сами понимаете.",
        "Малая капа, большая сеть, внимательная команда. Не упустите.",
        "Пока другие гоняются за шумом, $CULO копится на TON.",
        "Нативный токен CuloTon — и мы только разогреваемся.",
    ],
    "pl": [
        "TON cicho buduje, $CULO jedzie razem z nim.",
        "Wczesny memecoin na jednej z najszybszych sieci. Wiecie, o co chodzi.",
        "Mała kapa, duża sieć, czujna ekipa. Nie przegapcie.",
        "Inni gonią szum, $CULO składa się na TON.",
        "Natywny token CuloTon — to dopiero rozgrzewka.",
    ],
    "de": [
        "TON baut still weiter, $CULO fährt mit.",
        "Früher Memecoin auf einer der schnellsten Chains. Ihr wisst Bescheid.",
        "Small cap, großer Chain, aufmerksame Crew. Nicht verschlafen.",
        "Andere jagen Lärm — $CULO baut auf TON.",
        "Der native Token von CuloTon — und wir fangen gerade erst an.",
    ],
}


def mcap_notify(token: str, chat_id: str) -> int:
    import random
    data = fetch_culo_data()
    if not data or data["price"] is None:
        print("Could not fetch $CULO data from GeckoTerminal — skipping.", file=sys.stderr)
        return 0  # soft skip — don't fail the workflow

    pulse_emoji = "📈" if (data["change_h24"] or 0) >= 0 else "📉"
    parts = [
        f"📊 <b>$CULO MARKET PULSE</b>",
        "",
        f"💵 <b>Price:</b> {fmt_money(data['price'])}",
        f"{pulse_emoji} <b>24h:</b> {fmt_change(data['change_h24'])}",
        f"💼 <b>FDV:</b> {fmt_money(data['valuation'])}",
        f"🔄 <b>Vol 24h:</b> {fmt_money(data['vol_h24'])}",
        "",
    ]
    for loc in LOCALES:
        line = random.choice(FOMO_LINES[loc])
        parts.append(f"{FLAGS[loc]} <i>{html.escape(line)}</i>")
    parts.append("")
    if data.get("pool_addr"):
        parts.append(f"🔗 <a href=\"https://www.geckoterminal.com/{GECKO_NET}/pools/{data['pool_addr']}\">Chart on GeckoTerminal</a>")
    parts.append(f"💎 <b>CA:</b> <code>{CULO_CONTRACT}</code>")
    parts.append(f"📰 <a href=\"{SITE}/culo\">Token info on CuloTon</a>")

    text = "\n".join(parts)
    if len(text) > TG_MAX_LEN:
        text = text[: TG_MAX_LEN - 3] + "..."
    status, body = tg_send(token, chat_id, text)
    try:
        ok = json.loads(body).get("ok", False) if status == 200 else False
    except Exception:
        ok = False
    if not ok:
        print(f"mcap notify failed: status={status} body={body}", file=sys.stderr)
        return 1
    print(f"mcap posted: price={data['price']} fdv={data['valuation']} change={data['change_h24']}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=("deploy", "news", "mcap"))
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
    if args.mode == "mcap":
        return mcap_notify(token, chat_id)
    return news_notify(token, chat_id)


if __name__ == "__main__":
    sys.exit(main())
