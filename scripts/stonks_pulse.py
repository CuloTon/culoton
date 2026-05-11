"""Stonks chat pulse — community summary 3× daily.

Reads the last ~8h of messages from the public chat
@stonksonton via Telegram MTProto (Telethon, user-account session)
and asks Haiku to compose a "what was discussed" summary in 4
languages. Writes 4 markdown files per slot to web/src/content/pulse/
and posts a short EN teaser to our @cscriber_bot Telegram chat.

Slots (UTC):
  morning    — fired ~08:00, covers 00:00–08:00
  afternoon  — fired ~16:00, covers 08:00–16:00
  overnight  — fired ~00:00, covers 16:00–24:00 of previous day

Idempotent: if a file already exists for (date, slot), the run is a
no-op (so retries / reruns are safe).

Required env:
  TG_API_ID, TG_API_HASH, TG_USER_SESSION   — MTProto credentials
  ANTHROPIC_API_KEY                          — for the Haiku rewrite
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID       — to post the teaser
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
PULSE_DIR = ROOT / "web" / "src" / "content" / "pulse"
SITE = "https://culoton.fun"
CHAT_USERNAME = "stonksonton"
LOOKBACK_HOURS = 8
MAX_MESSAGES = 800
MAX_TRANSCRIPT_CHARS = 30000  # safety cap on input to Haiku
MODEL = "claude-haiku-4-5-20251001"
LOCALES = ("en", "ru", "pl", "de", "es", "uk")

SLOTS = ("morning", "afternoon", "overnight")
SLOT_LABEL = {
    "morning": "Morning Pulse",
    "afternoon": "Afternoon Pulse",
    "overnight": "Overnight Pulse",
}

CULOSCRIBE_SYSTEM = """You are CuloScribe — the editorial AI for CuloTon, an independent news desk covering the TON ecosystem.

Today you are writing a **community pulse**: a snapshot of what just happened in the public sTONks Telegram chat (t.me/stonksonton). Your job is to give a reader who missed the last 8 hours of chat a sharp, accurate, useful summary.

REQUIREMENTS:
- Lead with the 2-3 dominant topics. What did people actually talk about?
- Capture key opinions and tensions — if there was a debate, name both sides.
- Quote handles directly when it sharpens the point. Use the exact handle as it appears (e.g. @someone_eth). Do not invent handles.
- Mention notable claims (price calls, alpha tips, project mentions, technical concerns) — but flag speculation as speculation, never as fact.
- Skip pure noise (gm, gn, single emojis, bot announcements, "wen moon" spam).
- Keep it editorial: confident, dry, factual. No hype language ("massive", "to the moon"). No financial advice.
- Each language version is a NATIVE rewrite, not a translation. The same facts, but the words are CuloScribe's, locale-appropriate.

OUTPUT FORMAT — JSON ONLY, no prose around it:
{
  "en": { "title": "...", "summary": "...", "body_md": "...", "key_topics": ["..."], "participants": ["@h1", "@h2", ...] },
  "ru": { "title": "...", "summary": "...", "body_md": "...", "key_topics": ["..."], "participants": ["@h1", "@h2", ...] },
  "pl": { "title": "...", "summary": "...", "body_md": "...", "key_topics": ["..."], "participants": ["@h1", "@h2", ...] },
  "de": { "title": "...", "summary": "...", "body_md": "...", "key_topics": ["..."], "participants": ["@h1", "@h2", ...] },
  "es": { "title": "...", "summary": "...", "body_md": "...", "key_topics": ["..."], "participants": ["@h1", "@h2", ...] },
  "uk": { "title": "...", "summary": "...", "body_md": "...", "key_topics": ["..."], "participants": ["@h1", "@h2", ...] }
}

- title: punchy, max 80 chars, no clickbait
- summary: one sentence, max 200 chars
- body_md: 3-5 paragraphs, plain markdown, no top-level # heading (the page renders its own h1)
- key_topics: 2-5 short topic strings
- participants: handles that meaningfully contributed (max 12), reused across all six locales
- es = Spanish, uk = Ukrainian — each a native rewrite, not a translation
"""


def slot_for_now(now: datetime) -> str:
    """Map current UTC hour to a slot."""
    h = now.hour
    if 6 <= h < 14:
        return "morning"
    if 14 <= h < 22:
        return "afternoon"
    return "overnight"


def slot_window(slot: str, now: datetime) -> tuple[datetime, datetime, str]:
    """Return (start, end, date_label) for a slot. Lookback up to LOOKBACK_HOURS."""
    end = now
    start = end - timedelta(hours=LOOKBACK_HOURS)
    # date_label: YYYY-MM-DD of the END of the slot
    date_label = end.strftime("%Y-%m-%d")
    return start, end, date_label


def existing_path(date_label: str, slot: str, locale: str) -> Path:
    return PULSE_DIR / locale / f"{date_label}-{slot}.md"


def already_done(date_label: str, slot: str) -> bool:
    return existing_path(date_label, slot, "en").exists()


# ---------- Telethon: read public chat ------------------------------------

async def fetch_chat_messages(start: datetime, end: datetime) -> list[dict]:
    from telethon import TelegramClient
    from telethon.sessions import StringSession

    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]
    session = os.environ["TG_USER_SESSION"]

    out: list[dict] = []
    async with TelegramClient(StringSession(session), api_id, api_hash) as client:
        try:
            entity = await client.get_entity(CHAT_USERNAME)
        except Exception as e:
            print(f"  Cannot resolve chat {CHAT_USERNAME}: {e}", file=sys.stderr)
            return []
        async for m in client.iter_messages(entity, limit=MAX_MESSAGES):
            mdate = m.date.astimezone(timezone.utc) if m.date else None
            if not mdate:
                continue
            if mdate < start:
                break
            if mdate > end:
                continue
            text = (m.text or "").strip()
            if not text:
                continue
            sender = await m.get_sender()
            handle = None
            if sender:
                if getattr(sender, "username", None):
                    handle = "@" + sender.username
                else:
                    parts = []
                    if getattr(sender, "first_name", None):
                        parts.append(sender.first_name)
                    if getattr(sender, "last_name", None):
                        parts.append(sender.last_name)
                    handle = " ".join(parts) or "anon"
            else:
                handle = "anon"
            out.append({
                "date": mdate,
                "handle": handle,
                "text": text,
            })
    out.reverse()  # oldest first for chronological reading
    return out


def build_transcript(messages: list[dict]) -> str:
    """Render messages into a token-efficient transcript."""
    lines: list[str] = []
    total = 0
    for m in messages:
        ts = m["date"].strftime("%H:%M")
        line = f"[{ts}] {m['handle']}: {m['text']}"
        # crude truncation per-line to avoid one essay eating the budget
        if len(line) > 700:
            line = line[:700] + "…"
        if total + len(line) > MAX_TRANSCRIPT_CHARS:
            lines.append(f"... [transcript truncated at {len(lines)} messages] ...")
            break
        lines.append(line)
        total += len(line) + 1
    return "\n".join(lines)


# ---------- Haiku: rewrite -------------------------------------------------

def call_haiku(transcript: str, slot: str, date_label: str) -> dict | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").lstrip("﻿").strip()
    if not api_key:
        print("ANTHROPIC_API_KEY missing.", file=sys.stderr)
        return None
    client = Anthropic(api_key=api_key)
    user_prompt = (
        f"SLOT: {slot} of {date_label} (UTC). Window: last {LOOKBACK_HOURS}h of @{CHAT_USERNAME}.\n\n"
        f"CHAT TRANSCRIPT:\n{transcript}\n\n"
        "Now produce the JSON in the exact format from the system instructions."
    )
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2400,
            system=CULOSCRIBE_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as e:
        print(f"Haiku call failed: {e}", file=sys.stderr)
        return None
    parts = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    raw = "".join(parts).strip()
    # Extract first JSON object
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        print(f"No JSON in Haiku response. Raw: {raw[:400]}", file=sys.stderr)
        return None
    try:
        return json.loads(m.group(0))
    except Exception as e:
        print(f"JSON parse failed: {e}\nRaw: {raw[:400]}", file=sys.stderr)
        return None


# ---------- Markdown writer ------------------------------------------------

def write_locale_files(
    payload: dict,
    *,
    slot: str,
    date_label: str,
    end_dt: datetime,
    message_count: int,
) -> list[Path]:
    out: list[Path] = []
    for loc in LOCALES:
        block = payload.get(loc) or {}
        title = (block.get("title") or "").strip()
        summary = (block.get("summary") or "").strip()
        body = (block.get("body_md") or "").strip()
        topics = block.get("key_topics") or []
        participants = block.get("participants") or []
        if not title or not summary or not body:
            print(f"  Skipping {loc}: incomplete payload.", file=sys.stderr)
            continue
        fm = {
            "locale": loc,
            "slot": slot,
            "title": title,
            "summary": summary,
            "date": end_dt.isoformat(),
            "source_chat": f"t.me/{CHAT_USERNAME}",
            "message_count": int(message_count),
            "participants": list(participants)[:24],
            "tags": ["pulse", "stonks", "community"] + [t for t in topics if isinstance(t, str)][:5],
        }
        path = existing_path(date_label, slot, loc)
        path.parent.mkdir(parents=True, exist_ok=True)
        fm_yaml = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
        path.write_text(f"---\n{fm_yaml}---\n\n{body}\n", encoding="utf-8")
        out.append(path)
    return out


# ---------- TG teaser post -------------------------------------------------

def post_teaser(payload: dict, *, slot: str, date_label: str, msg_count: int) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("TG creds missing — skipping teaser post.", file=sys.stderr)
        return
    en = (payload.get("en") or {})
    title = (en.get("title") or "").strip() or f"sTONks Pulse — {SLOT_LABEL[slot]}"
    summary = (en.get("summary") or "").strip()
    slug = f"{date_label}-{slot}"
    url = f"{SITE}/pulse/{slug}/"
    text = (
        f"📡 <b>sTONks Pulse — {SLOT_LABEL[slot]}</b>\n\n"
        f"<b>{html.escape(title)}</b>\n\n"
        f"{html.escape(summary)}\n\n"
        f"<i>{msg_count} messages from @{CHAT_USERNAME} in the last {LOOKBACK_HOURS}h.</i>\n\n"
        f"👉 <a href=\"{url}\">Read on culoton.fun</a>"
    )
    import urllib.parse
    import urllib.request
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"TG teaser: HTTP {r.status}")
    except Exception as e:
        print(f"TG teaser failed: {e}", file=sys.stderr)


# ---------- Main -----------------------------------------------------------

async def main_async(slot_arg: str | None) -> int:
    load_dotenv(ROOT / ".env")
    now = datetime.now(timezone.utc)
    slot = slot_arg or slot_for_now(now)
    if slot not in SLOTS:
        print(f"Unknown slot: {slot}", file=sys.stderr)
        return 2

    start, end, date_label = slot_window(slot, now)
    print(f"Pulse run — slot={slot} window={start.isoformat()} → {end.isoformat()}")

    if already_done(date_label, slot):
        print(f"  {date_label}-{slot} already on disk — no-op.")
        return 0

    if not os.environ.get("TG_API_ID") or not os.environ.get("TG_API_HASH") or not os.environ.get("TG_USER_SESSION"):
        print("TG_API_ID / TG_API_HASH / TG_USER_SESSION missing — pipeline offline.", file=sys.stderr)
        return 0

    messages = await fetch_chat_messages(start, end)
    print(f"  Fetched {len(messages)} messages from @{CHAT_USERNAME}.")
    if len(messages) < 5:
        print("  Too few messages to summarise — skipping this slot.")
        return 0

    transcript = build_transcript(messages)
    payload = call_haiku(transcript, slot, date_label)
    if not payload:
        print("  Haiku rewrite failed — aborting.")
        return 1

    written = write_locale_files(
        payload,
        slot=slot,
        date_label=date_label,
        end_dt=end,
        message_count=len(messages),
    )
    print(f"  Wrote {len(written)} files: {[p.name for p in written]}")

    post_teaser(payload, slot=slot, date_label=date_label, msg_count=len(messages))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", choices=list(SLOTS), default=None,
                        help="Override slot (default: derived from current UTC hour).")
    args = parser.parse_args()
    return asyncio.run(main_async(args.slot))


if __name__ == "__main__":
    sys.exit(main())
