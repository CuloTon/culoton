"""One-time bootstrap: register bot commands + description with Telegram.

Run manually after the workflow lands:
  TELEGRAM_BOT_TOKEN=... python scripts/tg_set_commands.py

This populates the in-app "/" autocomplete menu in @cscriber_bot
and sets the about-bot blurb shown when users tap on the bot info.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.telegram.org/bot"

COMMANDS = [
    {"command": "help", "description": "Show all commands"},
    {"command": "news", "description": "Top 5 stories from the last 6h"},
    {"command": "blog", "description": "Latest CuloScribe roundup"},
    {"command": "price", "description": "Live $TON or $CULO market data"},
    {"command": "ask", "description": "Ask CuloScribe anything (AI Q&A)"},
    {"command": "points", "description": "Your activity score"},
    {"command": "leaderboard", "description": "Top 10 active members this week"},
]

DESCRIPTION = (
    "CuloScribe — editorial AI for CuloTon, covering the TON ecosystem "
    "24/7. Hit /help for the full command list. Top 3 active members each "
    "week win prizes. culoton.fun"
)

SHORT_DESCRIPTION = (
    "TON-ecosystem news desk. /help for commands. Earn points, win weekly prizes."
)


def call(token: str, method: str, payload: dict) -> dict | None:
    url = f"{API_BASE}{token}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  {method} HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  {method} failed: {e}", file=sys.stderr)
        return None


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN missing — can't set commands.", file=sys.stderr)
        return 2

    r1 = call(token, "setMyCommands", {"commands": json.dumps(COMMANDS)})
    print("setMyCommands:", r1)
    r2 = call(token, "setMyDescription", {"description": DESCRIPTION})
    print("setMyDescription:", r2)
    r3 = call(token, "setMyShortDescription", {"short_description": SHORT_DESCRIPTION})
    print("setMyShortDescription:", r3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
