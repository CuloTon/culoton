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
            "No active members this week — no winner, no payout. The board resets now.\n\n"
            "🎁 <b>#1 next week wins 5 TON.</b> Tap the daily quiz, use /ask, /news — earn pts. "
            "/help for commands."
        )

    medals = ["🥇", "🥈", "🥉"]
    lines = [f"🏆 <b>WEEKLY LEADERBOARD</b> {range_label}\n"]
    for i, (_uid, rec) in enumerate(top):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = html.escape(rec.get("username") or "anon")
        pts = rec.get("weekly_points", 0)
        lines.append(f"{medal} <b>{name}</b> — {pts} pts")

    winner_name = html.escape(top[0][1].get("username") or "anon")
    lines.append(
        f"\n🏆 <b>{winner_name} wins 5 TON this week.</b> The CuloTon team will reach out for your wallet address.\n"
        "Board resets now — new week, new shot. Daily quiz at 15:00 UTC, /help for commands."
    )
    return "\n".join(lines)


def build_admin_dm(state: dict) -> str:
    """Private DM for the project owner — full top-10 with user_ids
    so prizes can be sent off-platform. Sent BEFORE the weekly reset.
    """
    top = top_weekly(state, n=10)
    week_started = state.get("week_started_at", "")
    week_label = ""
    try:
        wdt = datetime.fromisoformat(week_started)
        week_label = wdt.strftime("%Y-%m-%d")
    except Exception:
        pass
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not top:
        return (
            "🎁 <b>Weekly winners — admin DM</b>\n\n"
            f"Period: {week_label} → {today} UTC\n\n"
            "No active members this week. Nothing to distribute."
        )

    lines = [
        "🎁 <b>Weekly winners — admin DM</b>",
        f"Period: {week_label} → {today} UTC",
        "Pełna lista top 10 do dystrybucji nagród (top 3 publicznie ogłoszone na kanale):",
        "",
    ]
    for i, (uid, rec) in enumerate(top):
        name = html.escape(rec.get("username") or "anon")
        pts = rec.get("weekly_points", 0)
        total = rec.get("total_points", 0)
        prefix = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
        lines.append(f"{prefix} <b>{name}</b> — {pts} pts (all-time {total}) · uid <code>{uid}</code>")
    lines.append("")
    lines.append("After this DM the weekly board is reset.")
    return "\n".join(lines)


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    admin_chat_id = os.environ.get("ADMIN_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Missing TG creds — weekly recap is a no-op.", file=sys.stderr)
        return 0

    state = load_state()

    # 1) Public channel announcement (top 3, no user IDs — privacy)
    text = build_announcement(state)
    print(f"Posting weekly recap to public chat {chat_id} (top entries: "
          f"{len(top_weekly(state, 3))}).")
    tg_send(token, chat_id, text)

    # 2) Private admin DM with full top 10 + user IDs — for prize distribution
    if admin_chat_id:
        dm_text = build_admin_dm(state)
        print(f"Sending admin DM with full winners list to {admin_chat_id}.")
        tg_send(token, admin_chat_id, dm_text)
    else:
        print("ADMIN_CHAT_ID not set — skipping private winners DM.")

    # 3) Reset weekly counter
    reset_weekly(state)
    save_state(state)
    print("Weekly_points reset for all users.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
