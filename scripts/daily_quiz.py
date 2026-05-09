"""CuloTon daily TON quiz — generates one multiple-choice question
about the TON ecosystem and posts it to the public TG channel.

Pipeline:
  1. Asks Claude Haiku for a single TON-themed quiz question with 4 options
     (A/B/C/D) and the correct letter. Strict JSON output.
  2. Stores the quiz state in data/quizzes.json keyed by UTC date — the
     bot reads this when handling /quiz <answer> from users.
  3. Posts the question to the public TG channel with instructions to
     DM @cscriber_bot with /quiz <letter> to win 20 points (daily cap).
  4. Idempotent — second invocation on the same UTC day is a no-op.

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


def render_quiz_message(quiz: dict) -> str:
    opts = quiz["options"]
    body = (
        "🧩 <b>DAILY TON QUIZ</b>\n\n"
        f"<b>{html.escape(quiz['question'])}</b>\n\n"
        f"🅰  {html.escape(opts['A'])}\n"
        f"🅱  {html.escape(opts['B'])}\n"
        f"🅲  {html.escape(opts['C'])}\n"
        f"🅳  {html.escape(opts['D'])}\n\n"
        f"👇 Tap your answer — <b>+{QUIZ_REWARD} pts</b> for correct, one shot per user, midnight UTC deadline.\n"
        "🏆 <b>Weekly winner gets 5 TON</b> — first payout <b>Sunday 17 May 20:00 UTC</b>, every Sunday after that. /leaderboard"
    )
    return body


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
    args = p.parse_args()

    if not _strip_bom(os.getenv("ANTHROPIC_API_KEY")):
        print("ANTHROPIC_API_KEY missing — skipping (no-op).")
        return 0

    today = _today_key()
    quizzes = load_quizzes()
    if not args.dry_run and today in quizzes:
        print(f"Quiz already posted for {today} — skipping.")
        return 0

    topic = random.choice(TOPIC_POOL)
    seed = f"{today}-{random.randint(1000, 9999)}"
    print(f"Generating quiz (topic={topic!r}, seed={seed})...")

    quiz = call_haiku_for_quiz(topic, seed)
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

    body = render_quiz_message(quiz)
    keyboard = build_inline_keyboard(today)
    status, resp = tg_send_with_keyboard(token, chat_id, body, keyboard)
    if status != 200:
        print(f"quiz tg post failed: status={status} body={resp}", file=sys.stderr)
        return 1

    quizzes[today] = quiz
    save_quizzes(quizzes)
    print(f"Quiz posted for {today} and persisted (with inline-keyboard buttons).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
