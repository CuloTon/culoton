"""One-shot local helper to mint a Telethon StringSession.

WHY: the stonks-pulse pipeline reads messages from the public chat
@stonksonton via the Telegram MTProto API (user account, not the
bot account). MTProto needs a persistent session, and that session
can only be created interactively (phone code, optional 2FA). So
we generate it once on the user's local machine and stash the
resulting string in a GitHub Secret.

USAGE (run on your laptop, not in CI):

    set TG_API_ID=<id from my.telegram.org>
    set TG_API_HASH=<hash from my.telegram.org>
    python scripts/tg_user_session_setup.py

You'll be prompted for:
  • phone number (e.g. +48...)
  • the SMS / Telegram code Telegram sends you
  • your 2FA password if 2FA is enabled

The script prints a session string. Copy it and add it to GitHub
Secrets as TG_USER_SESSION (along with TG_API_ID and TG_API_HASH).
"""

from __future__ import annotations

import os
import sys

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
except Exception:
    print("Install telethon first:  pip install telethon", file=sys.stderr)
    raise


def main() -> int:
    api_id_raw = os.environ.get("TG_API_ID", "").strip()
    api_hash = os.environ.get("TG_API_HASH", "").strip()
    if not api_id_raw or not api_hash:
        print("Set TG_API_ID and TG_API_HASH from https://my.telegram.org/apps first.", file=sys.stderr)
        return 2
    try:
        api_id = int(api_id_raw)
    except ValueError:
        print(f"TG_API_ID must be numeric, got {api_id_raw!r}", file=sys.stderr)
        return 2

    print("Logging in to Telegram (this is interactive — phone, code, optional 2FA)...")
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        s = client.session.save()
        print("\nSESSION STRING (add as TG_USER_SESSION secret):\n")
        print(s)
        print("\nDone. Treat the string like a password — it logs in as you.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
