"""Weekly leaderboard announcement + reset.

Cron-fired Sunday 20:00 UTC by .github/workflows/tg-weekly-recap.yml.
Posts the top-3 active members to TELEGRAM_CHAT_ID, then zeroes
weekly_points and stamps a fresh week_started_at.
"""

from __future__ import annotations

import html
import os
import sys
from datetime import datetime, timezone

from _tg_points import load_state, reset_weekly, save_state, top_weekly
from tg_bot_interact import tg_send


def build_announcement(state: dict) -> str:
    top = top_weekly(state, n=3)
    week_started = state.get("week_started_at", "")
    week_label = ""
    try:
        wdt = datetime.fromisoformat(week_started)
        week_label = wdt.strftime("%b %d")
    except Exception:
        pass
    today = datetime.now(timezone.utc).strftime("%b %d")
    range_label = f"({week_label} → {today} UTC)" if week_label else ""

    if not top:
        return (
            "🏆 <b>Weekly leaderboard</b> " + range_label + "\n\n"
            "No active members this week. The board resets now — "
            "be first next week. Try /news, /price ton, or /ask "
            "&lt;your question&gt;.\n\n"
            "🎁 Top 3 each week receive prizes."
        )

    medals = ["🥇", "🥈", "🥉"]
    lines = [f"🏆 <b>WEEKLY LEADERBOARD</b> {range_label}\n"]
    for i, (_uid, rec) in enumerate(top):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = html.escape(rec.get("username") or "anon")
        pts = rec.get("weekly_points", 0)
        lines.append(f"{medal} <b>{name}</b> — {pts} pts")
    lines.append(
        "\n🎁 Congrats! The CuloTon team will reach out about your prize.\n"
        "Board resets now — new week, new shot. /help for commands."
    )
    return "\n".join(lines)


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Missing TG creds — weekly recap is a no-op.", file=sys.stderr)
        return 0

    state = load_state()
    text = build_announcement(state)
    print(f"Posting weekly recap to chat {chat_id} (top entries: "
          f"{len(top_weekly(state, 3))}).")
    tg_send(token, chat_id, text)

    reset_weekly(state)
    save_state(state)
    print("Weekly_points reset for all users.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
