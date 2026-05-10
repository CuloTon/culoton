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
⚠️ <b>CULO TON RELAUNCH</b>

We are <b>relaunching</b>. Following consultations with senior figures in
the TON ecosystem who endorsed the project as developmental, a new version
of the token is rolling out. The requirement from those talks: a
<b>tax-free token</b>. The previous contract is being retired.

➡️ New ticker: <code>$CULOTON</code>
➡️ New CA: <i>will be announced here after deployment</i>
➡️ Current investors: please <b>sell your existing $CULO holdings</b>
   ahead of the migration.

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
