"""CuloTon Daily Take generator.

Once a day, posts a short, dry, FT-style editorial take on the TON
ecosystem to the public TG channel and (if X drafts are wired) the X
drafts chat. The script reads the freshest 10 EN news for context,
asks Claude Haiku for one take in CuloScribe voice, and posts.

Idempotent — uses scripts/announced.db with kind='meme' (kept for
backward-compat with previously-announced rows) and the date as the
slug.

Graceful no-op when ANTHROPIC_API_KEY or TELEGRAM_BOT_TOKEN is missing.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import random
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import yaml  # noqa: F401  -- transitively used by parse_frontmatter

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS_DIR))
from telegram_notify import (  # noqa: E402
    db_init,
    already_announced,
    mark_announced,
    parse_frontmatter,
    tg_send,
    SITE,
    TG_MAX_LEN,
)

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
RETRY_LIMIT = 2
NEWS_CONTEXT_COUNT = 10

FORMATS = [
    "single-sentence dry observation about today's TON state, max 140 chars",
    "two-line contrast: setup → punch (e.g. 'They said X. Then Y happened.'), max 180 chars total",
    "mock-headline style — write it like an FT headline that's secretly a take, max 120 chars",
    "POV-style reaction (e.g. 'POV: you bought $X at $Y — three days later'), max 160 chars",
    "single-line dry comparison between TON and another chain, max 140 chars",
]

CAPTION_SYSTEM = """You are CuloScribe — the editorial AI for CuloTon, an independent news desk covering the TON blockchain.

Today you are not writing news. You are writing ONE TAKE — a single short, sharp, dry observation that the desk's TG channel can post.

# Voice
Witty journalist with an edge — Financial Times that secretly knows what a memecoin is. Dry, observational, never cringe, never begging, never "wagmi". Humour lives in dry phrasing or in the truth itself, never in jokes about TON or holders. The reader should chuckle, then think.

# Hard rules
- ONE take. Not three options. Pick the best one and ship.
- Stay tight: format-prescribed length max. Better short than padded.
- $CULOTON can be mentioned at MOST once, lightly. The take is a TON observation, not a token shill.
- No exclamation marks. No "🚀". No "🌙". No "to the moon". No "wagmi". No "ngmi". No "anon". Treat each of those as forbidden words. Pump emoji are forbidden.
- One emoji at the start is fine if it sharpens the line. Otherwise zero.
- No price predictions. No financial advice. Observation, not call.

# Output
Strict JSON, no prose outside JSON, no code fences:
{
  "take": "the take text exactly as it should appear",
  "format_used": "name of the format you picked from the menu"
}"""

CAPTION_USER_TEMPLATE = """Write today's take for the CuloTon desk's TG channel.

Today's context (the freshest TON ecosystem news; don't summarise it, just let it inform what's relevant right now):

{news_block}

Format menu (pick ONE that fits today's mood):
{format_menu}

Today's seed for variety: {seed}

Write the take now. Strict JSON only."""


def _strip_bom(s: str | None) -> str:
    return (s or "").lstrip("﻿").strip()


def collect_recent_en_news(limit: int) -> list[tuple[str, dict]]:
    en_dir = NEWS_DIR / "en"
    if not en_dir.exists():
        return []
    items: list[tuple[str, dict]] = []
    for path in en_dir.glob("*.md"):
        try:
            fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not fm.get("date") or not fm.get("title"):
            continue
        items.append((path.name, fm))
    items.sort(key=lambda x: str(x[1].get("date", "")), reverse=True)
    return items[:limit]


def build_news_block(items: list[tuple[str, dict]]) -> str:
    lines = []
    for idx, (_, fm) in enumerate(items, 1):
        lines.append(f"{idx}. {fm.get('title', '').strip()} — {fm.get('summary', '').strip()}")
    return "\n".join(lines) if lines else "(no recent news available)"


def call_haiku_for_take(news_block: str, seed: str) -> dict:
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("anthropic SDK not installed — pip install anthropic")
    client = Anthropic(api_key=_strip_bom(os.getenv("ANTHROPIC_API_KEY")))

    format_menu = "\n".join(f"- {f}" for f in FORMATS)
    user = CAPTION_USER_TEMPLATE.format(news_block=news_block, format_menu=format_menu, seed=seed)

    last_err = None
    for attempt in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=400,
                system=CAPTION_SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            take = (data.get("take") or data.get("meme") or "").strip()
            if not take:
                raise ValueError("empty take")
            return {"take": take, "format_used": data.get("format_used", "?")}
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Take generation failed after {RETRY_LIMIT + 1} attempts: {last_err}")


def post_take_to_tg(token: str, chat_id: str, take: str) -> bool:
    body = (
        "💬 <b>DAILY TAKE</b>\n\n"
        f"<i>{html.escape(take)}</i>\n\n"
        "— CuloScribe AI · CuloTon Desk\n"
        f'🌐 <a href="{SITE}">culoton.fun</a> · $CULOTON'
    )
    if len(body) > TG_MAX_LEN:
        body = body[: TG_MAX_LEN - 3] + "..."
    status, resp = tg_send(token, chat_id, body, disable_preview=True)
    if status != 200:
        print(f"take tg post failed: status={status} body={resp}", file=sys.stderr)
        return False
    return True


def post_take_as_x_draft(take: str) -> None:
    tg_token = _strip_bom(os.getenv("TELEGRAM_BOT_TOKEN"))
    drafts_chat = (os.getenv("X_DRAFTS_CHAT_ID") or "").strip()
    if not tg_token or not drafts_chat:
        return

    tweet = f"{take}\n\n#TON #CULOTON"
    if len(tweet) > 280:
        tweet = take[: 280 - len("\n\n#TON #CULOTON") - 1].rstrip() + "\n\n#TON #CULOTON"

    intent_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(tweet, safe="")
    body = (
        f"📝 <b>X DRAFT — Daily take</b>  ({len(tweet)}/280)\n\n"
        f"<pre>{html.escape(tweet)}</pre>\n\n"
        f'→ <a href="{intent_url}">Open in X (1 tap to post)</a>'
    )
    status, resp = tg_send(tg_token, drafts_chat, body, disable_preview=True)
    if status != 200:
        print(f"take X draft failed: status={status} body={resp}", file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Generate and print, do not post or mark")
    args = p.parse_args()

    if not _strip_bom(os.getenv("ANTHROPIC_API_KEY")):
        print("ANTHROPIC_API_KEY missing — skipping (no-op).")
        return 0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = f"{today}-take"

    conn = db_init()
    if not args.dry_run and already_announced(conn, slug, "meme"):
        print(f"Take already posted today ({slug}) — skipping.")
        return 0

    items = collect_recent_en_news(NEWS_CONTEXT_COUNT)
    news_block = build_news_block(items)
    seed = f"{today}-{random.randint(1000, 9999)}"
    print(f"Generating take (seed={seed}, ctx={len(items)} articles)...")

    result = call_haiku_for_take(news_block, seed)
    take = result["take"]
    print(f"Format: {result['format_used']}")
    print(f"Take: {take}")

    if args.dry_run:
        print("(dry-run: not posting, not marking)")
        return 0

    token = _strip_bom(os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing — skipping (no-op).")
        return 0

    if not post_take_to_tg(token, chat_id, take):
        return 1

    post_take_as_x_draft(take)

    mark_announced(conn, slug, "meme")
    print(f"Posted daily take for {today}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
