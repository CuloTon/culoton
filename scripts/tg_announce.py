"""Ad-hoc admin broadcast to the public TG group.

Posts the message in $ANNOUNCE_TEXT verbatim (Telegram parse_mode=HTML)
to TELEGRAM_CHAT_ID. Triggered manually via the tg-announce.yml workflow
(workflow_dispatch `message` input). Graceful no-op when creds or text
are missing so a misfire never errors the pipeline.

Reusable: any one-off announcement (contest results, schedule changes,
launches) can go out this way without touching the automated notifiers.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from telegram_notify import tg_send  # noqa: E402


def _clean(s: str | None) -> str:
    return (s or "").lstrip("﻿").strip()


def tg_send_photo(token: str, chat_id: str, photo_url: str, caption: str) -> tuple[int, str]:
    """Post a photo by URL with HTML caption. Telegram fetches the photo itself."""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def main() -> int:
    token = _clean(os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = _clean(os.getenv("TELEGRAM_CHAT_ID"))
    # Allow a literal "\n" in the input to mean a newline (some dispatch
    # paths flatten multi-line strings); real newlines pass through fine.
    text = (os.getenv("ANNOUNCE_TEXT") or "").replace("\\n", "\n").strip()
    photo = _clean(os.getenv("ANNOUNCE_PHOTO_URL"))

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing — skipping (no-op).")
        return 0
    if not text:
        print("ANNOUNCE_TEXT empty — nothing to post (no-op).")
        return 0

    if photo:
        # Caption max 1024 chars. Trim if needed to keep the call from 400-ing.
        caption = text if len(text) <= 1024 else text[:1020] + "…"
        status, body = tg_send_photo(token, chat_id, photo, caption)
        if status != 200:
            print(f"announce photo failed: status={status} body={body}", file=sys.stderr)
            return 1
        print(f"Announcement (photo + caption) posted: {photo} | {len(caption)} chars.")
        return 0

    status, body = tg_send(token, chat_id, text, disable_preview=True)
    if status != 200:
        print(f"announce failed: status={status} body={body}", file=sys.stderr)
        return 1
    print(f"Announcement posted ({len(text)} chars).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
