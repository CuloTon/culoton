"""Shared activity-points storage for the interactive TG bot.

Point data lives in data/points.json so it is committed alongside
news/seen.db state and survives between GitHub Actions runs.

Schema:
{
  "users": {
    "<user_id>": {
      "username": "<handle or first_name>",
      "total_points": int,
      "weekly_points": int,
      "last_command_at": "<iso timestamp>",
      "daily_points": int,
      "daily_day": "<YYYY-MM-DD>",
      "last_ask_at": "<iso timestamp>",
      "last_msg_point_at": "<iso timestamp>"
    }
  },
  "week_started_at": "<iso timestamp>"
}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
POINTS_PATH = ROOT / "data" / "points.json"
OFFSET_PATH = ROOT / "data" / "tg_offset.txt"

DAILY_POINT_CAP = 20
ASK_COOLDOWN_SEC = 180  # 3 minutes between /ask uses per user

# Plain chat messages in the group earn a small activity point, rate-limited
# so chatting normally pays but burst-spamming does not. The daily cap (20)
# still bounds the total either way.
MSG_POINT_REWARD = 1
MSG_POINT_COOLDOWN_SEC = 90  # at most one message-point per 90s per user

# Accounts hidden from the public activity leaderboard (the dev / team
# accounts, the bot, etc.). Matched case-insensitively against the stored
# display name with a leading "@" stripped. Their points are still tracked
# — they just don't appear in /leaderboard or the standings recap.
LEADERBOARD_EXCLUDE = {"culodaddy_ton"}


def is_excluded_from_leaderboard(rec: dict) -> bool:
    name = (rec.get("username") or "").strip().lstrip("@").lower()
    return name in LEADERBOARD_EXCLUDE


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_state() -> dict[str, Any]:
    if not POINTS_PATH.exists():
        return {"users": {}, "week_started_at": _now_iso()}
    try:
        return json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"users": {}, "week_started_at": _now_iso()}


def save_state(state: dict[str, Any]) -> None:
    POINTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    POINTS_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def load_offset() -> int:
    if not OFFSET_PATH.exists():
        return 0
    try:
        return int(OFFSET_PATH.read_text(encoding="utf-8").strip() or 0)
    except Exception:
        return 0


def save_offset(offset: int) -> None:
    OFFSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_PATH.write_text(str(offset), encoding="utf-8")


def get_user(state: dict, user_id: int, display_name: str) -> dict:
    """Return (and lazily create) the user record. Updates display name."""
    users = state.setdefault("users", {})
    key = str(user_id)
    rec = users.get(key)
    if rec is None:
        rec = {
            "username": display_name,
            "total_points": 0,
            "weekly_points": 0,
            "last_command_at": "",
            "daily_points": 0,
            "daily_day": "",
            "last_ask_at": "",
        }
        users[key] = rec
    if display_name and display_name != rec.get("username"):
        rec["username"] = display_name
    return rec


def award_points(rec: dict, amount: int) -> int:
    """Add up to `amount` points respecting the daily cap.

    Returns the number of points actually awarded (may be 0 if cap reached).
    """
    today = _today_key()
    if rec.get("daily_day") != today:
        rec["daily_day"] = today
        rec["daily_points"] = 0

    remaining = DAILY_POINT_CAP - rec["daily_points"]
    granted = max(0, min(amount, remaining))
    if granted > 0:
        rec["daily_points"] += granted
        rec["weekly_points"] = rec.get("weekly_points", 0) + granted
        rec["total_points"] = rec.get("total_points", 0) + granted
    rec["last_command_at"] = _now_iso()
    return granted


def can_use_ask(rec: dict) -> tuple[bool, int]:
    """Returns (allowed, seconds_remaining_until_next_ask)."""
    last = rec.get("last_ask_at") or ""
    if not last:
        return True, 0
    try:
        last_dt = datetime.fromisoformat(last)
    except Exception:
        return True, 0
    now = datetime.now(timezone.utc)
    elapsed = (now - last_dt).total_seconds()
    if elapsed >= ASK_COOLDOWN_SEC:
        return True, 0
    return False, int(ASK_COOLDOWN_SEC - elapsed)


def mark_ask(rec: dict) -> None:
    rec["last_ask_at"] = _now_iso()


def can_earn_msg_point(rec: dict) -> tuple[bool, int]:
    """Returns (allowed, seconds_remaining) for awarding a plain-message point."""
    last = rec.get("last_msg_point_at") or ""
    if not last:
        return True, 0
    try:
        last_dt = datetime.fromisoformat(last)
    except Exception:
        return True, 0
    elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
    if elapsed >= MSG_POINT_COOLDOWN_SEC:
        return True, 0
    return False, int(MSG_POINT_COOLDOWN_SEC - elapsed)


def mark_msg_point(rec: dict) -> None:
    rec["last_msg_point_at"] = _now_iso()


def top_weekly(state: dict, n: int = 10) -> list[tuple[str, dict]]:
    users = state.get("users", {})
    items = [
        (uid, rec) for uid, rec in users.items()
        if rec.get("weekly_points", 0) > 0 and not is_excluded_from_leaderboard(rec)
    ]
    items.sort(key=lambda x: x[1].get("weekly_points", 0), reverse=True)
    return items[:n]


def reset_weekly(state: dict) -> None:
    for rec in state.get("users", {}).values():
        rec["weekly_points"] = 0
    state["week_started_at"] = _now_iso()
