"""CuloTon TON quiz — generates one multiple-choice question about the TON
ecosystem and posts it (with A/B/C/D inline buttons) to the public TG group.

Auto-posted several times a day via .github/workflows/daily-quiz.yml — one
quiz per (UTC day, slot), where slot ∈ {morning, midday, afternoon, evening}
is derived from the current UTC hour (override with --slot).

Pipeline:
  1. Asks Claude Haiku for a single easy TON-themed question, 4 options,
     correct letter, explanation. Strict JSON.
  2. Stores it in data/quizzes.json under key "YYYY-MM-DD-<slot>" — the
     interactive bot reads this for /quiz <letter> and for the inline-button
     callbacks ("quiz:<YYYY-MM-DD-slot>:<letter>"). Old flat "YYYY-MM-DD"
     keys from the single-daily era still resolve for stale callbacks.
  3. Posts the question + a top-10 weekly leaderboard to the group.
  4. Idempotent — a second invocation for the same (day, slot) is a no-op.

Graceful no-op when ANTHROPIC_API_KEY or TELEGRAM_BOT_TOKEN is missing.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
QUIZZES_PATH = ROOT / "data" / "quizzes.json"

sys.path.insert(0, str(SCRIPTS_DIR))
from telegram_notify import tg_send, SITE  # noqa: E402  -- still imported for fallback
import _tg_points  # noqa: E402  -- weekly leaderboard, posted alongside the quiz
from _tg_points import QUIZ_SLOTS, quiz_slot_for_now  # noqa: E402
import urllib.error
import urllib.parse
import urllib.request

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
RETRY_LIMIT = 2
QUIZ_REWARD = 20  # one full daily cap — quiz is the highest-value daily action

TOPIC_POOL = [
    "Telegram and TON basics — what Telegram is, what TON stands for, what Toncoin is, why they're connected",
    "Big-name TON ecosystem projects at a glance — what Notcoin / Hamster Kombat / Getgems / STON.fi / Tonkeeper / Blum each do in one sentence",
    "TON brand history at a high level — who started Telegram, where TON came from, what 'TON Foundation' does",
    "Everyday crypto terms used in TON in plain English — wallet, jetton (= TON's word for 'token'), NFT, memcoin, staking",
    "Telegram Mini-Apps as a concept — what they are, why they grew so fast, examples people have heard of",
    "Common-sense facts about TON the user would pick up by hanging in the community for a week",
]

SYSTEM = """You are a quiz master writing one multiple-choice question for a knowledgeable TON-blockchain audience.

# Hard rules
- ONE question. Four options (A, B, C, D). Exactly one correct.
- Topic must be FACTUAL and verifiable. Avoid speculation, opinions, or trick questions.
- Difficulty: EASY. Anyone who follows TON casually or has used Telegram should be able to answer. Aim for the kind of question someone playing on the bus during their commute can solve in 5 seconds.
- AVOID: specific dates, exact percentages, internal protocol details (Catchain version, sharding parameters, FunC syntax, validator counts), niche project trivia, "first to launch X" gotchas. Those are out.
- PREFER: basic ecosystem knowledge — what Telegram is, what TON is, what Toncoin is, big-name projects (Notcoin, Getgems, STON.fi, Tonkeeper) and what they do at the highest level, "which company is behind X", "what does this acronym mean".
- All four options must be plausible distractors of similar plausibility. No throwaway joke options.
- Question stem and options stay short — under 80 chars each.
- The correct answer must NOT always be option B. Distribute randomly.
- DO NOT invent facts. If unsure about a specific number/date, pick a more fundamental angle.

# Output
Strict JSON, no prose outside JSON, no code fences:
{
  "question": "the question stem, ending with a question mark",
  "options": {
    "A": "option text",
    "B": "option text",
    "C": "option text",
    "D": "option text"
  },
  "correct": "A" | "B" | "C" | "D",
  "explanation": "one short sentence explaining why the correct answer is correct"
}"""

USER_TEMPLATE = """Write one TON-blockchain quiz question on this topic:

{topic}

Today's seed for variety: {seed}

Strict JSON only."""


def _strip_bom(s: str | None) -> str:
    return (s or "").lstrip("﻿").strip()


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_quizzes() -> dict:
    if not QUIZZES_PATH.exists():
        return {}
    try:
        return json.loads(QUIZZES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_quizzes(data: dict) -> None:
    QUIZZES_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUIZZES_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def call_haiku_for_quiz(topic: str, seed: str) -> dict:
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("anthropic SDK not installed")
    client = Anthropic(api_key=_strip_bom(os.getenv("ANTHROPIC_API_KEY")))

    user = USER_TEMPLATE.format(topic=topic, seed=seed)
    last_err = None
    for _ in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=600,
                system=SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            if not isinstance(data.get("options"), dict):
                raise ValueError("options not an object")
            for letter in ("A", "B", "C", "D"):
                if not data["options"].get(letter):
                    raise ValueError(f"missing option {letter}")
            if data.get("correct") not in ("A", "B", "C", "D"):
                raise ValueError(f"invalid correct: {data.get('correct')}")
            if not data.get("question"):
                raise ValueError("missing question")
            return data
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Quiz generation failed after {RETRY_LIMIT + 1} attempts: {last_err}")


_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def render_leaderboard_block() -> str:
    """Top-10 of the current week's standings, formatted for the quiz message.

    Read-only: pulls from data/points.json (maintained by the interactive bot).
    Returns an empty string if there are no scores yet this week.
    """
    try:
        state = _tg_points.load_state()
        top = _tg_points.top_weekly(state, 10)
    except Exception:
        return ""
    if not top:
        return (
            "\n\n━━━━━━━━━━━━━\n"
            "🏆 <b>THIS WEEK'S TOP 10</b> — no scores yet. Be first: answer the quiz, post, use /ask.\n"
            "<i>Weekly winner takes 5 TON — payout every Sunday 20:00 UTC.</i>"
        )
    lines = ["\n\n━━━━━━━━━━━━━", "🏆 <b>THIS WEEK'S TOP 10</b> (resets Sun 20:00 UTC)"]
    for i, (_uid, rec) in enumerate(top, 1):
        name = (rec.get("username") or "anon").strip()
        if name and not name.startswith("@") and " " not in name:
            name = "@" + name
        rank = _MEDALS.get(i, f"{i}.")
        lines.append(f"{rank} {html.escape(name)} — <b>{rec.get('weekly_points', 0)}</b>")
    lines.append("<i>Top spot wins 5 TON — payout every Sunday 20:00 UTC. /leaderboard</i>")
    return "\n".join(lines)


def render_quiz_message(quiz: dict, slot: str = "") -> str:
    opts = quiz["options"]
    title = f"🧩 <b>TON QUIZ — {slot.upper()}</b>" if slot else "🧩 <b>TON QUIZ</b>"
    body = (
        f"{title}\n\n"
        f"<b>{html.escape(quiz['question'])}</b>\n\n"
        f"🅰  {html.escape(opts['A'])}\n"
        f"🅱  {html.escape(opts['B'])}\n"
        f"🅲  {html.escape(opts['C'])}\n"
        f"🅳  {html.escape(opts['D'])}\n\n"
        f"👇 Tap your answer — <b>+{QUIZ_REWARD} pts</b> for a correct one (subject to the 20 pts/day cap), "
        "one shot per quiz, deadline midnight UTC. New quiz a few times a day — different question each time.\n"
        "💬 <b>Activity counts too</b> — every message in the group is scored. But spamming to farm points = ban — "
        "post something worth reading.\n"
        "🏆 <b>Weekly top scorer gets 5 TON</b> — payout every Sunday 20:00 UTC."
    )
    return body + render_leaderboard_block()


def build_inline_keyboard(date_key: str) -> dict:
    """4 buttons in a 2x2 grid. callback_data parsed by tg_bot_interact."""
    def btn(letter: str) -> dict:
        return {"text": letter, "callback_data": f"quiz:{date_key}:{letter}"}
    return {
        "inline_keyboard": [
            [btn("A"), btn("B")],
            [btn("C"), btn("D")],
        ],
    }


def tg_send_with_keyboard(token: str, chat_id: str, text: str, keyboard: dict) -> tuple[int, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
        "reply_markup": json.dumps(keyboard, ensure_ascii=False),
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Generate and print, do not post or persist")
    p.add_argument("--slot", choices=QUIZ_SLOTS, help="Override the slot (default: derived from current UTC hour)")
    args = p.parse_args()

    if not _strip_bom(os.getenv("ANTHROPIC_API_KEY")):
        print("ANTHROPIC_API_KEY missing — skipping (no-op).")
        return 0

    today = _today_key()
    slot = args.slot or quiz_slot_for_now()
    quiz_key = f"{today}-{slot}"
    quizzes = load_quizzes()
    if not args.dry_run and quiz_key in quizzes:
        print(f"Quiz already posted for {quiz_key} — skipping.")
        return 0

    topic = random.choice(TOPIC_POOL)
    seed = f"{quiz_key}-{random.randint(1000, 9999)}"
    print(f"Generating quiz (slot={slot}, topic={topic!r}, seed={seed})...")

    quiz = call_haiku_for_quiz(topic, seed)
    quiz["slot"] = slot
    quiz["posted_at"] = datetime.now(timezone.utc).isoformat()
    quiz["answered"] = {}

    print(f"Q: {quiz['question']}")
    print(f"   A) {quiz['options']['A']}")
    print(f"   B) {quiz['options']['B']}")
    print(f"   C) {quiz['options']['C']}")
    print(f"   D) {quiz['options']['D']}")
    print(f"Correct: {quiz['correct']}")
    print(f"Explanation: {quiz.get('explanation', '?')}")

    if args.dry_run:
        print("(dry-run: not posting, not persisting)")
        return 0

    token = _strip_bom(os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing — skipping (no-op).")
        return 0

    body = render_quiz_message(quiz, slot)
    keyboard = build_inline_keyboard(quiz_key)
    status, resp = tg_send_with_keyboard(token, chat_id, body, keyboard)
    if status != 200:
        print(f"quiz tg post failed: status={status} body={resp}", file=sys.stderr)
        return 1

    quizzes[quiz_key] = quiz
    save_quizzes(quizzes)
    print(f"Quiz posted for {quiz_key} and persisted (with inline-keyboard buttons).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
