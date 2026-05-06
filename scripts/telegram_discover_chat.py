"""Helper: list chat IDs the bot has seen.

Usage (after creating the bot with BotFather, adding it to your group
as admin, and posting any message in that group so the bot is aware):

    python scripts/telegram_discover_chat.py <BOT_TOKEN>

It calls getUpdates and prints every distinct chat with id, type and
title. Group chat IDs are negative numbers — that is the value to use
as TELEGRAM_CHAT_ID secret. Channel IDs start with -100.
"""

from __future__ import annotations

import json
import sys
import urllib.request


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/telegram_discover_chat.py <BOT_TOKEN>", file=sys.stderr)
        return 1
    token = sys.argv[1].strip()
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"API call failed: {e}", file=sys.stderr)
        return 1
    if not data.get("ok"):
        print(f"Telegram returned error: {data}", file=sys.stderr)
        return 1

    seen: dict[int, dict] = {}
    for upd in data.get("result", []):
        msg = upd.get("message") or upd.get("edited_message") or upd.get("channel_post") or {}
        chat = msg.get("chat") or {}
        cid = chat.get("id")
        if cid is None or cid in seen:
            continue
        seen[cid] = chat

    if not seen:
        print("No chats seen yet. Make sure the bot has been added to the group")
        print("AND that someone has posted a message there after the bot joined.")
        return 1

    print("Chats the bot has seen:\n")
    for cid, chat in seen.items():
        kind = chat.get("type", "?")
        title = chat.get("title") or chat.get("username") or chat.get("first_name") or "(unnamed)"
        print(f"  chat_id = {cid}    type = {kind:<10} title = {title}")
    print("\nUse the 'chat_id' of your CuloTon group as the TELEGRAM_CHAT_ID secret.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
