"""Posts the CULO TON relaunch notice to the project Telegram chat.

Reads TG_BOT_TOKEN and TG_CHAT_ID from env. No-ops cleanly when either is
missing so the GitHub workflow stays green until secrets are configured.

Posts an English-only message asking holders of the previous $CULO
contract to sell, citing the no-tax requirement that came out of
consultations with senior figures in the TON ecosystem.

Usage (local):  python scripts/telegram_relaunch_post.py
Usage (CI):     same, with TG_BOT_TOKEN and TG_CHAT_ID secrets set
"""

from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request


MESSAGE = """\
✅ <b>$CULOTON IS LIVE</b>

The new tax-free <b>$CULOTON</b> contract is deployed on TON.

➡️ Ticker: <code>$CULOTON</code>
➡️ Contract: <code>EQAYaqIikryTucQEz3IGRC62M7Eo4rzvduFAV5iWZ1b0A2Uc</code>
➡️ Tonviewer: https://tonviewer.com/EQAYaqIikryTucQEz3IGRC62M7Eo4rzvduFAV5iWZ1b0A2Uc

This is the <b>new</b> contract — the previous $CULO is retired. From here
on, $CULOTON is the live token of the project.

🌐 culoton.fun/culo
"""


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — nothing to do.", flush=True)
        return 0

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": MESSAGE,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"Telegram response {resp.status}: {body[:300]}", flush=True)
            return 0 if 200 <= resp.status < 300 else 1
    except Exception as exc:
        print(f"Telegram post failed: {exc!r}", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
