"""Ad-hoc admin broadcast to the public TG group.

Posts the message in $ANNOUNCE_TEXT verbatim (Telegram parse_mode=HTML)
to TELEGRAM_CHAT_ID. Triggered manually via the tg-announce.yml workflow
(workflow_dispatch `message` input). Graceful no-op when creds or text
are missing so a misfire never errors the pipeline.

Reusable: any one-off announcement (contest results, schedule changes,
launches) can go out this way without touching the automated notifiers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from telegram_notify import tg_send  # noqa: E402


def _clean(s: str | None) -> str:
    return (s or "").lstrip("﻿").strip()


def main() -> int:
    token = _clean(os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = _clean(os.getenv("TELEGRAM_CHAT_ID"))
    # Allow a literal "\n" in the input to mean a newline (some dispatch
    # paths flatten multi-line strings); real newlines pass through fine.
    text = (os.getenv("ANNOUNCE_TEXT") or "").replace("\\n", "\n").strip()

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing — skipping (no-op).")
        return 0
    if not text:
        print("ANNOUNCE_TEXT empty — nothing to post (no-op).")
        return 0

    status, body = tg_send(token, chat_id, text, disable_preview=True)
    if status != 200:
        print(f"announce failed: status={status} body={body}", file=sys.stderr)
        return 1
    print(f"Announcement posted ({len(text)} chars).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
