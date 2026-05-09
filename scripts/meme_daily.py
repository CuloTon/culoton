"""CuloTon meme-of-the-day generator.

Once a day:
  1. Reads the freshest 10 EN news for context (so the meme reacts to
     what's actually happening in the TON ecosystem, not generic shilling).
  2. Asks Claude Haiku for a single short, witty meme in CuloScribe voice
     — dry observation, never cringe, rotating across a few formats so we
     don't repeat the same shape every day.
  3. Posts the meme to the public TG channel (TELEGRAM_CHAT_ID) and, if
     X drafts are configured, also creates a one-tap "Open in X" draft.
  4. Idempotent — uses scripts/announced.db with kind='meme' and the
     date as the slug, so a second invocation on the same day no-ops.

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
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
SCRIPTS_DIR = Path(__file__).resolve().parent

# Reuse the same announced.db that telegram_notify uses, so all
# announce-state lives in one place. New kind: 'meme'.
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

MODEL = "claude-haiku-4-5-20251001"
RETRY_LIMIT = 2
NEWS_CONTEXT_COUNT = 10

# Format hints — AI picks one for variety. Keep these tight; the longer
# the format pool the more drift in voice. These all share CuloScribe's
# dry, FT-with-edge register — never goofy, never begging.
FORMATS = [
    "single-sentence dry observation about today's TON state, max 140 chars",
    "two-line contrast: setup → punch (e.g. 'They said X. Then Y happened.'), max 180 chars total",
    "mock-headline style — write it like an FT headline that's secretly a meme, max 120 chars",
    "POV-style reaction (e.g. 'POV: you bought $X at $Y — three days later'), max 160 chars",
    "single-line dry comparison between TON and another chain, max 140 chars",
]

SYSTEM = """You are CuloScribe — the editorial AI for CuloTon, an independent news desk covering the TON blockchain.

Today you are not writing news. You are writing ONE MEME — a single short, sharp, dry observation that the desk's TG channel can post.

# Voice
Witty journalist with an edge — Financial Times that secretly knows what a memecoin is. Dry, observational, never cringe, never begging, never "wagmi". Humour lives in dry phrasing or in the truth itself, never in jokes about TON or holders. The reader should chuckle, then think.

# Hard rules
- ONE meme. Not three options. Pick the best one and ship.
- Stay tight: format-prescribed length max. Better short than padded.
- $CULO can be mentioned at MOST once, lightly. The meme is a TON observation, not a token shill.
- No exclamation marks. No "🚀". No "🌙". No "to the moon". No "wagmi". No "ngmi". No "anon". Treat each of those as forbidden words. Pump emoji are forbidden.
- One emoji at the start is fine if it sharpens the line. Otherwise zero.
- No price predictions. No financial advice. Observation, not call.

# Output
Strict JSON, no prose outside JSON, no code fences:
{
  "meme": "the meme text exactly as it should appear",
  "format_used": "name of the format you picked from the menu"
}"""

USER_TEMPLATE = """Write today's meme for the CuloTon desk's TG channel.

Today's context (the freshest TON ecosystem news; don't summarise it, just let it inform what's relevant right now):

{news_block}

Format menu (pick ONE that fits today's mood):
{format_menu}

Today's seed for variety: {seed}

Write the meme now. Strict JSON only."""


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


def call_haiku_for_meme(news_block: str, seed: str) -> dict:
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("anthropic SDK not installed — pip install anthropic")
    client = Anthropic()

    format_menu = "\n".join(f"- {f}" for f in FORMATS)
    user = USER_TEMPLATE.format(news_block=news_block, format_menu=format_menu, seed=seed)

    last_err = None
    for attempt in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=400,
                system=SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            meme = (data.get("meme") or "").strip()
            if not meme:
                raise ValueError("empty meme")
            return {"meme": meme, "format_used": data.get("format_used", "?")}
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Meme generation failed after {RETRY_LIMIT + 1} attempts: {last_err}")


def post_meme_to_tg(token: str, chat_id: str, meme: str) -> bool:
    body = (
        "😏 <b>MEME OF THE DAY</b>\n\n"
        f"<i>{html.escape(meme)}</i>\n\n"
        "— CuloScribe AI · CuloTon Desk\n"
        f'🌐 <a href="{SITE}">culoton.fun</a> · $CULO'
    )
    if len(body) > TG_MAX_LEN:
        body = body[: TG_MAX_LEN - 3] + "..."
    status, resp = tg_send(token, chat_id, body, disable_preview=True)
    if status != 200:
        print(f"meme tg post failed: status={status} body={resp}", file=sys.stderr)
        return False
    return True


def post_meme_as_x_draft(meme: str) -> None:
    """If X drafts are wired up, also send the meme as an X draft so the
    user can one-tap publish it on X. No-op if not configured.
    """
    tg_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    drafts_chat = (os.getenv("X_DRAFTS_CHAT_ID") or "").strip()
    if not tg_token or not drafts_chat:
        return

    tweet = f"{meme}\n\n#TON #CULOTON"
    if len(tweet) > 280:
        tweet = meme[: 280 - len("\n\n#TON #CULOTON") - 1].rstrip() + "\n\n#TON #CULOTON"

    intent_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(tweet, safe="")
    body = (
        f"📝 <b>X DRAFT — Meme of the day</b>  ({len(tweet)}/280)\n\n"
        f"<pre>{html.escape(tweet)}</pre>\n\n"
        f'→ <a href="{intent_url}">Open in X (1 tap to post)</a>'
    )
    status, resp = tg_send(tg_token, drafts_chat, body, disable_preview=True)
    if status != 200:
        print(f"meme X draft failed: status={status} body={resp}", file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Generate and print, do not post or mark")
    args = p.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY missing — skipping (no-op).")
        return 0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = f"{today}-meme"

    conn = db_init()
    if not args.dry_run and already_announced(conn, slug, "meme"):
        print(f"Meme already posted today ({slug}) — skipping.")
        return 0

    items = collect_recent_en_news(NEWS_CONTEXT_COUNT)
    news_block = build_news_block(items)
    seed = f"{today}-{random.randint(1000, 9999)}"
    print(f"Generating meme (seed={seed}, ctx={len(items)} articles)...")

    result = call_haiku_for_meme(news_block, seed)
    meme = result["meme"]
    print(f"Format: {result['format_used']}")
    print(f"Meme: {meme}")

    if args.dry_run:
        print("(dry-run: not posting, not marking)")
        return 0

    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing — skipping (no-op).")
        return 0

    if not post_meme_to_tg(token, chat_id, meme):
        return 1

    post_meme_as_x_draft(meme)

    mark_announced(conn, slug, "meme")
    print(f"Posted meme for {today}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
