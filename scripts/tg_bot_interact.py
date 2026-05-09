"""Interactive Telegram bot for CuloTon community.

Polled every 2 minutes from .github/workflows/tg-interact.yml.

Reads pending updates via getUpdates with persistent offset
(data/tg_offset.txt), routes /commands, awards activity points
(data/points.json), and replies in English.

Commands:
  /start, /help        — welcome + command list
  /news                — top 5 EN stories from the last 6h
  /blog                — link to the latest CuloScribe roundup
  /price ton|culo      — live market data
  /ask <question>      — Haiku Q&A grounded in the latest 50 EN news
  /points              — caller's score
  /leaderboard         — top 10 active members this week + prize info

A daily cap (20 points / user / day) prevents farming.
/ask is rate-limited to once every 3 minutes per user (paid API).
"""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from _culo_market import fetch_culo_data, fmt_change, fmt_money
from _tg_points import (
    award_points,
    can_use_ask,
    get_user,
    load_offset,
    load_state,
    mark_ask,
    save_offset,
    save_state,
    top_weekly,
)

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
BLOG_DIR = ROOT / "web" / "src" / "content" / "blog"
SITE = "https://culoton.fun"
QUIZZES_PATH = ROOT / "data" / "quizzes.json"
QUIZ_REWARD = 20  # one daily cap — quiz is the highest-value daily action

TG_API_TIMEOUT = 35  # > long-poll timeout below, with margin
LONG_POLL_TIMEOUT = 25  # seconds; getUpdates returns immediately on new msg
GET_UPDATES_LIMIT = 100
LOOP_BUDGET_SEC = 270  # 4.5 minutes — leaves margin under workflow's 6-min cap
NEWS_FOR_LIST_HOURS = 6
NEWS_FOR_LIST_MAX = 5
ASK_CONTEXT_NEWS_COUNT = 50
ASK_MAX_QUESTION_CHARS = 400

ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
ASK_COOLDOWN_MIN = 3
ASK_COOLDOWN_NOTE = (
    f"ℹ <i>I answer once every {ASK_COOLDOWN_MIN} minutes per user — "
    "the AI engine costs us money, the cooldown keeps the lights on.</i>"
)

COMMANDS_HELP = (
    "👋 <b>Welcome to CuloTon Desk</b>\n"
    "I'm <b>@cscriber_bot</b> — the editorial AI for CuloTon, "
    "covering the TON ecosystem 24/7.\n\n"
    "📰 <b>News</b>\n"
    "/news — top 5 stories from the last 6h\n"
    "/blog — latest CuloScribe roundup\n\n"
    "💰 <b>Market</b>\n"
    "/price ton — live $TON price\n"
    "/price culo — $CULO market data\n\n"
    "🤖 <b>Ask me anything</b>\n"
    "/ask &lt;question&gt; — anything about TON, CuloTon, $CULO or sTONks; "
    f"light small-talk welcome too. <b>Limit: 1 per {ASK_COOLDOWN_MIN} min per user.</b>\n\n"
    "🧩 <b>Daily quiz</b>\n"
    "Tap A/B/C/D under the daily quiz post — drops every day at 15:00 UTC. "
    f"Correct = +{QUIZ_REWARD} pts (subject to daily cap), one shot per user.\n"
    "🏆 <b>Weekly winner gets 5 TON</b> — top of the leaderboard every Sunday 20:00 UTC.\n\n"
    "🏆 <b>Activity & rewards</b>\n"
    "/points — your activity score\n"
    "/leaderboard — top 10 most active members this week\n"
    "ℹ The top 3 active members each week get rewards "
    "(announced every Sunday).\n\n"
    "🌐 <a href=\"https://culoton.fun\">culoton.fun</a>"
)


# ---------- Knowledge baked into /ask ---------------------------------------

CULOTON_FACTS = """\
CULOTON / $CULO — ground truth (always reply in English).

PLATFORM
- CuloTon (https://culoton.fun) is an English-language news desk covering the
  TON Blockchain ecosystem. It is the editorial layer built around the $CULO
  memecoin: legitimate TON content first, $CULO surfaced as the platform's
  native token (banner, /culo page, branding).
- Multilingual: every story exists in EN, RU, PL and DE — same slug, native
  re-reporting (not translation) by CuloScribe.
- Cadence: ~24 news items/day, plus 3 editorial roundups every day
  (morning ~08:00 PL, noon ~13:00, evening ~19:00). Archive at /archive.
- Stack (for the curious): Astro static site, Python ingest, Claude Haiku
  rewrites, GitHub Actions cron, FTP deploy to seohost.pl. Logos and code on
  github.com/CuloTon.

PERSONA
- You are CuloScribe — the AI editor. Witty, dry, professional. Never break
  character to mention you are Claude.

$CULO TOKEN
- Memecoin on TON. Contract: EQD5dCm196cT60OTcCz_MI_f_QtpZYGU5mazX-4rjAOHiKrJ
- Track record: ~10,000X market-cap move on Polygon (2024), follow-through on
  SUI, now launched on TON in 2026 with this dedicated platform.
- Launched via the stonks.pump Deploy-with-TAX tokenomic (fixed supply + small
  buy/sell tax) — NOT a bonding curve.
- Brand: born from a long-running cross-chain meme; community-driven.

CHANNELS
- Web: https://culoton.fun
- Telegram (this bot): @cscriber_bot
- Telegram community: https://t.me/culoton
- X / Twitter: https://x.com/culoton_

EDITORIAL RULES
- Never give specific financial advice ("buy now", "price will hit X"). You
  can describe what is happening; recommendations are off-limits.
- Never invent prices, dates, contract addresses, or quotes not present in
  FACTS or NEWS CONTEXT. If unsure, say so.
"""

STONKS_FACTS = """\
sTONks / stonks.pump — ground truth.

WHAT IT IS
- sTONks (https://stonksbots.com) is a four-stage on-chain pipeline on TON:
  1. BUILD — agentic LLM pipelines (Claude/GPT/Gemini/Grok) write code,
     humans review.
  2. DEPLOY — one-click to managed infra, VPS, bare metal, Telegram Cloud or
     LLM APIs. Encrypted secrets, autoscaling.
  3. TOKENIZE — fairlaunch, presale, bonding curve, revshare, dividends, or
     fully custom tokenomics. Or no token, just crypto payments.
  4. GOVERN — Roundtable DAO with an AI Oracle that audits commits, deploys,
     milestones against the on-chain roadmap.

PUBLISHED METRICS
- 2,170 projects launched. 12,000+ monthly active traders. 41,300 TON in
  ecosystem liquidity. 160,000 TON in dividends paid to holders.

TRADING STACK
- Trading Terminal: multi-wallet, sniper, TradingView, limit orders, on-chain
  fills, sub-100ms execution.
- @stonks_sniper_bot — full terminal inside Telegram DM.
- Stonks Gem Bot + New Pairs Bot — alpha alerts, no gatekeeping.

REAL-WORLD-ASSET BINDING
- Every token launched is cryptographically bound on-chain to its GitHub repo.
- Holders watch real commits land. AI Oracle verifies progress for closed
  source projects too. Supply / fees / curves locked at launch — no hidden
  mints, no dev unlocks, no rug levers.

stonks.pump — THE LAUNCHPAD
- Free TON jetton launchpad inside sTONks. Two liquidity modes:
  * Seed LP — you provide the LP yourself; cost = LP + 4 TON; 5% of tax
    revenue to launchpad; ~5 min processing.
  * Virtual LP — algorithmic, ~500 TON-equivalent liquidity for a flat
    3.2 TON fee; 1-2 min processing.
- Tokenomics: Simple coin (no tax) or Customize (buy/sell tax up to 30% each,
  anti-sniper limits, dev bag max 5%, marketing wallet, holder rewards).
- Built-in protections: LP burn, auto ownership revoke, anti-sniper rules,
  single-tx LP add.
- Walkthrough: youtube.com/watch?v=IaodzcNhy_4
- Launch via @stonks_sniper_bot or stonkslabs.com/launch/ton
- Manual: stonks-bot.gitbook.io/stonks-bot-manual/stonks.pump-launchpad

$CULO RELATION
- $CULO was deployed on stonks.pump using Deploy-with-TAX (fixed supply, small
  buy/sell tax). The CuloTon news desk was built afterwards as the editorial
  layer around the token.
"""


# ---------- Telegram API ----------------------------------------------------

def tg_api(token: str, method: str, payload: dict) -> dict | None:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TG_API_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  TG {method} HTTP {e.code}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  TG {method} failed: {e}", file=sys.stderr)
        return None


def tg_send(token: str, chat_id: int | str, text: str, *, reply_to: int | None = None) -> dict | None:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
        payload["allow_sending_without_reply"] = "true"
    return tg_api(token, "sendMessage", payload)


def tg_get_updates(token: str, offset: int, timeout: int = 0) -> list[dict]:
    payload = {
        "offset": offset,
        "limit": GET_UPDATES_LIMIT,
        "timeout": timeout,
        "allowed_updates": json.dumps(["message", "callback_query"]),
    }
    resp = tg_api(token, "getUpdates", payload)
    if not resp or not resp.get("ok"):
        return []
    return resp.get("result", [])


def tg_answer_callback(token: str, callback_query_id: str, text: str, show_alert: bool = True) -> dict | None:
    """Reply privately to a button click — only the clicker sees the popup."""
    payload = {
        "callback_query_id": callback_query_id,
        "text": text[:200],  # Telegram caps callback alerts at 200 chars
        "show_alert": "true" if show_alert else "false",
    }
    return tg_api(token, "answerCallbackQuery", payload)


# ---------- Content helpers -------------------------------------------------

def parse_frontmatter(md_text: str) -> dict:
    if not md_text.startswith("---"):
        return {}
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        return {}


def latest_news(n: int, hours: int | None = None) -> list[dict]:
    en = NEWS_DIR / "en"
    if not en.exists():
        return []
    cutoff = None
    if hours is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items: list[tuple[datetime, dict]] = []
    for path in en.glob("*.md"):
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        d = fm.get("date")
        if not d:
            continue
        try:
            dt = d if isinstance(d, datetime) else datetime.fromisoformat(str(d))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if cutoff and dt < cutoff:
            continue
        items.append((dt, {
            "slug": path.stem,
            "title": (fm.get("title") or "").strip(),
            "summary": (fm.get("summary") or "").strip(),
            "source_name": (fm.get("source_name") or "").strip(),
            "tags": fm.get("tags") or [],
            "date": dt,
        }))
    items.sort(key=lambda x: x[0], reverse=True)
    return [it[1] for it in items[:n]]


def latest_blog() -> dict | None:
    en = BLOG_DIR / "en"
    if not en.exists():
        return None
    items: list[tuple[datetime, dict]] = []
    for path in en.glob("*.md"):
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        d = fm.get("date")
        if not d:
            continue
        try:
            dt = d if isinstance(d, datetime) else datetime.fromisoformat(str(d))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        items.append((dt, {
            "slug": path.stem,
            "title": (fm.get("title") or "").strip(),
            "summary": (fm.get("summary") or "").strip(),
            "kind": (fm.get("kind") or "").strip(),
            "date": dt,
        }))
    if not items:
        return None
    items.sort(key=lambda x: x[0], reverse=True)
    return items[0][1]


# ---------- Market helpers --------------------------------------------------

def fetch_ton_price() -> dict | None:
    """CoinGecko free endpoint — TON price + 24h change."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CuloTon-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=TG_API_TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  CoinGecko TON fetch failed: {e}", file=sys.stderr)
        return None
    ton = (data or {}).get("the-open-network") or {}
    if not ton:
        return None
    return {
        "price": ton.get("usd"),
        "change_h24": ton.get("usd_24h_change"),
        "vol_h24": ton.get("usd_24h_vol"),
        "mcap": ton.get("usd_market_cap"),
    }


# ---------- Command handlers -----------------------------------------------

def cmd_help() -> str:
    return COMMANDS_HELP


def cmd_news() -> str:
    items = latest_news(NEWS_FOR_LIST_MAX, hours=NEWS_FOR_LIST_HOURS)
    if not items:
        # Fallback to the most recent overall, regardless of cutoff.
        items = latest_news(NEWS_FOR_LIST_MAX)
        if not items:
            return "📰 No news yet. Check back soon — new stories drop every 2 hours."
    lines = [f"📰 <b>Top {len(items)} stories — last {NEWS_FOR_LIST_HOURS}h</b>\n"]
    for it in items:
        url = f"{SITE}/news/{it['slug']}/"
        title = html.escape(it["title"])
        src = html.escape(it["source_name"]) if it["source_name"] else ""
        meta = f" — <i>{src}</i>" if src else ""
        lines.append(f"• <a href=\"{url}\">{title}</a>{meta}")
    return "\n".join(lines)


def cmd_blog() -> str:
    blog = latest_blog()
    if not blog:
        return "📓 No blog roundup yet. CuloScribe drops them 3× daily."
    url = f"{SITE}/blog/{blog['slug']}/"
    title = html.escape(blog["title"])
    summary = html.escape(blog["summary"])
    kind_emoji = {"morning": "⚡", "noon": "☀️", "evening": "🌅"}.get(blog.get("kind", ""), "📓")
    kind = (blog.get("kind") or "").upper() or "ROUNDUP"
    return (
        f"{kind_emoji} <b>CuloScribe — {kind}</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"{summary}\n\n"
        f"👉 <a href=\"{url}\">Read on culoton.fun</a>"
    )


def cmd_price(arg: str) -> str:
    asset = (arg or "").strip().lower()
    if asset in ("ton", "$ton", ""):
        d = fetch_ton_price()
        if not d or d.get("price") is None:
            return "💰 Couldn't reach the price feed right now. Try again in a minute."
        price = fmt_money(d["price"])
        change = fmt_change(d.get("change_h24"))
        vol = fmt_money(d.get("vol_h24"))
        mcap = fmt_money(d.get("mcap"))
        return (
            "💰 <b>$TON — live</b>\n\n"
            f"Price: <b>{price}</b> ({change} 24h)\n"
            f"Market cap: {mcap}\n"
            f"24h volume: {vol}\n\n"
            "Source: CoinGecko"
        )
    if asset in ("culo", "$culo"):
        d = fetch_culo_data()
        if not d or d.get("price") is None:
            return "💰 $CULO market data unavailable right now. Try again in a minute."
        price = fmt_money(d["price"])
        change = fmt_change(d.get("change_h24"))
        vol = fmt_money(d.get("vol_h24"))
        valuation = fmt_money(d.get("valuation"))
        return (
            "💰 <b>$CULO — live</b>\n\n"
            f"Price: <b>{price}</b> ({change} 24h)\n"
            f"FDV: {valuation}\n"
            f"24h volume: {vol}\n\n"
            "Source: GeckoTerminal"
        )
    return "Usage: /price ton  or  /price culo"


def cmd_ask(question: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").lstrip("﻿").strip()
    if not api_key:
        return "🤖 The /ask service is offline (missing API key)."
    if not question or len(question.strip()) < 5:
        return "🤖 Ask me a real question — e.g. <code>/ask why is TON pumping?</code>"
    if len(question) > ASK_MAX_QUESTION_CHARS:
        return f"🤖 Question is too long (max {ASK_MAX_QUESTION_CHARS} chars). Shorten and try again."

    try:
        from anthropic import Anthropic
    except Exception as e:
        return f"🤖 Q&A engine not installed on the runner: {e}"

    items = latest_news(ASK_CONTEXT_NEWS_COUNT)
    context_lines = []
    for it in items:
        date = it["date"].strftime("%Y-%m-%d")
        context_lines.append(
            f"[{date}] {it['title']} — {it['summary']} (source: {it['source_name']})"
        )
    context_block = "\n".join(context_lines) if context_lines else "(no recent news on file)"

    system = (
        "You are CuloScribe, the AI editor of CuloTon — a TON-blockchain news desk.\n"
        "\n"
        "WHAT YOU CAN ANSWER\n"
        "- Anything about the TON blockchain ecosystem (apps, protocols, news, "
        "trends, the chain itself).\n"
        "- Anything about CuloTon, the $CULO token, this Telegram bot, the news "
        "platform, the brand and our channels — see CULOTON FACTS below.\n"
        "- Anything about sTONks and the stonks.pump launchpad — see STONKS "
        "FACTS below.\n"
        "- Friendly small talk: greetings, how-are-you, weather, mood, light "
        "jokes. Keep it short (1-2 sentences) and on-vibe (dry CuloScribe wit).\n"
        "\n"
        "WHAT YOU MUST REFUSE (politely, then redirect to /news /price /blog or "
        "an on-topic question)\n"
        "- Specific financial advice ('should I buy', 'will price hit X', 'is "
        "this a good entry'). Describe what is happening, never recommend a "
        "trade. State you do not give financial advice.\n"
        "- Personal data, doxxing, anything invasive about the user, the team, "
        "or third parties.\n"
        "- NSFW, illegal, hateful, manipulative requests.\n"
        "- Off-topic rabbit holes unrelated to TON, CuloTon, sTONks or light "
        "small talk (politics, religion, medical, legal).\n"
        "\n"
        "STYLE\n"
        "- Always reply in ENGLISH, regardless of the language of the question.\n"
        "- Concise: 2-4 short paragraphs max. Plain prose, no bullet lists "
        "unless they truly help.\n"
        "- Confident, dry wit. End substantive answers with one short "
        "editorial take.\n"
        "- Do not invent prices, dates, contract addresses, or quotes that are "
        "not in FACTS or NEWS CONTEXT. If unsure, say so.\n"
        "- Never break character to mention you are Claude or any other model. "
        "You are CuloScribe.\n"
        "\n"
        "=== CULOTON FACTS ===\n"
        f"{CULOTON_FACTS}\n"
        "=== STONKS FACTS ===\n"
        f"{STONKS_FACTS}"
    )
    user_prompt = (
        f"NEWS CONTEXT (most recent first):\n{context_block}\n\n"
        f"USER QUESTION: {question.strip()}"
    )

    try:
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        answer = "".join(parts).strip() or "(no answer)"
    except Exception as e:
        return f"🤖 The Q&A call failed: {html.escape(str(e)[:240])}"

    return (
        f"🤖 <b>CuloScribe answers</b>\n\n"
        f"<i>Q: {html.escape(question.strip()[:200])}</i>\n\n"
        f"{html.escape(answer)}\n\n"
        f"{ASK_COOLDOWN_NOTE}"
    )


def cmd_quiz(user_id: str, arg: str) -> tuple[str, bool]:
    """Handle /quiz <answer>. Returns (reply_html, was_correct).

    Reads today's quiz from data/quizzes.json (posted earlier by
    daily_quiz.py via cron). Stores per-user answer to prevent retries.
    The actual points award happens in the dispatcher only when correct.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not QUIZZES_PATH.exists():
        return ("🧩 No quiz live yet. The first daily quiz drops at 15:00 UTC.", False)

    try:
        all_quizzes = json.loads(QUIZZES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return ("🧩 Quiz state unavailable, try again in a moment.", False)

    quiz = all_quizzes.get(today)
    if not quiz:
        return ("🧩 No quiz for today yet. Daily quiz drops at 15:00 UTC.", False)

    answer = arg.strip().upper()[:1]
    if answer not in ("A", "B", "C", "D"):
        return (
            "🧩 Send your answer letter — <code>/quiz A</code> (or B / C / D).\n\n"
            f"<b>{html.escape(quiz['question'])}</b>\n"
            f"🅰  {html.escape(quiz['options']['A'])}\n"
            f"🅱  {html.escape(quiz['options']['B'])}\n"
            f"🅲  {html.escape(quiz['options']['C'])}\n"
            f"🅳  {html.escape(quiz['options']['D'])}",
            False,
        )

    answered = quiz.setdefault("answered", {})
    if user_id and user_id in answered:
        prev = answered[user_id]
        verdict = "✅ correct" if prev["correct"] else "❌ wrong"
        return (
            f"🧩 You already played today — picked <b>{prev['answer']}</b> ({verdict}). "
            "Next quiz drops tomorrow at 15:00 UTC.",
            False,
        )

    correct = (answer == quiz["correct"])
    if user_id:
        answered[user_id] = {
            "answer": answer,
            "correct": correct,
            "answered_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            QUIZZES_PATH.parent.mkdir(parents=True, exist_ok=True)
            QUIZZES_PATH.write_text(
                json.dumps(all_quizzes, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"quiz state save failed: {e}", file=sys.stderr)

    if correct:
        explain = quiz.get("explanation", "")
        return (
            f"🧩 ✅ <b>Correct!</b> The answer was <b>{quiz['correct']}</b>.\n\n"
            f"<i>{html.escape(explain)}</i>\n\n"
            f"+{QUIZ_REWARD} pts (subject to daily cap of 20). See /points / /leaderboard.",
            True,
        )
    return (
        f"🧩 ❌ Not quite — your answer <b>{answer}</b> was wrong. "
        f"The correct answer was <b>{quiz['correct']}</b>. Try again tomorrow.",
        False,
    )


def cmd_points(rec: dict) -> str:
    name = html.escape(rec.get("username") or "you")
    return (
        f"🏆 <b>{name}</b>\n\n"
        f"This week: <b>{rec.get('weekly_points', 0)}</b> pts\n"
        f"All-time: <b>{rec.get('total_points', 0)}</b> pts\n"
        f"Today (cap 20): {rec.get('daily_points', 0)} pts\n\n"
        f"Use /leaderboard to see how you stack up."
    )


def cmd_leaderboard(state: dict) -> str:
    top = top_weekly(state, n=10)
    if not top:
        return (
            "🏆 <b>Weekly leaderboard</b>\n\n"
            "Nobody has earned points yet this week — "
            "be first. Try /news, /price ton, or /ask &lt;question&gt;."
        )
    lines = ["🏆 <b>Weekly leaderboard — top 10</b>\n"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (_uid, rec) in enumerate(top):
        pos = medals[i] if i < 3 else f"{i+1}."
        name = html.escape(rec.get("username") or "anon")
        pts = rec.get("weekly_points", 0)
        lines.append(f"{pos} <b>{name}</b> — {pts} pts")
    lines.append(
        "\n🎁 <b>#1 each week wins 5 TON</b> — winner announced every Sunday at 20:00 UTC."
    )
    return "\n".join(lines)


# ---------- Dispatch -------------------------------------------------------

def route_command(text: str) -> tuple[str, str]:
    """Return (command, argument). Strips bot mention if present."""
    body = text.strip()
    if not body.startswith("/"):
        return "", ""
    head, _, tail = body.partition(" ")
    cmd = head[1:].lower()
    if "@" in cmd:
        cmd = cmd.split("@", 1)[0]
    return cmd, tail.strip()


def points_for_command(cmd: str) -> int:
    if cmd == "ask":
        return 3
    if cmd in ("start", "help", "news", "blog", "price", "points", "leaderboard"):
        return 1
    return 0


def display_name(user: dict) -> str:
    if user.get("username"):
        return f"@{user['username']}"
    parts = []
    if user.get("first_name"):
        parts.append(user["first_name"])
    if user.get("last_name"):
        parts.append(user["last_name"])
    return " ".join(parts) or "anon"


def handle_quiz_callback(cb: dict, state: dict, token: str) -> None:
    """Handle a callback_query from a quiz inline-keyboard click.
    Replies privately via answerCallbackQuery (popup visible only to the clicker).
    Awards points on correct answer, enforces one-shot per user per quiz.
    """
    cbid = cb.get("id", "")
    data = (cb.get("data") or "").strip()
    from_user = cb.get("from") or {}

    # callback_data format: "quiz:<YYYY-MM-DD>:<A|B|C|D>"
    if not data.startswith("quiz:"):
        tg_answer_callback(token, cbid, "Unknown action.", show_alert=False)
        return

    parts = data.split(":")
    if len(parts) != 3 or parts[2] not in ("A", "B", "C", "D"):
        tg_answer_callback(token, cbid, "Invalid quiz button.", show_alert=False)
        return
    quiz_date = parts[1]
    answer = parts[2]

    if not from_user or from_user.get("is_bot"):
        tg_answer_callback(token, cbid, "?", show_alert=False)
        return

    user_id = str(from_user["id"])

    # Read quiz state
    if not QUIZZES_PATH.exists():
        tg_answer_callback(token, cbid, "🧩 Quiz state not available, try again later.", show_alert=True)
        return
    try:
        all_quizzes = json.loads(QUIZZES_PATH.read_text(encoding="utf-8"))
    except Exception:
        tg_answer_callback(token, cbid, "🧩 Quiz state unavailable.", show_alert=True)
        return

    quiz = all_quizzes.get(quiz_date)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not quiz:
        tg_answer_callback(token, cbid, "🧩 This quiz is no longer available.", show_alert=True)
        return
    if quiz_date != today:
        tg_answer_callback(token, cbid, "🧩 This quiz is closed — only today's counts.", show_alert=True)
        return

    answered = quiz.setdefault("answered", {})
    if user_id in answered:
        prev = answered[user_id]
        verdict = "✅ correct" if prev["correct"] else "❌ wrong"
        tg_answer_callback(
            token, cbid,
            f"🧩 You already answered: {prev['answer']} ({verdict}). Next quiz tomorrow 15:00 UTC.",
            show_alert=True,
        )
        return

    correct = (answer == quiz["correct"])
    answered[user_id] = {
        "answer": answer,
        "correct": correct,
        "answered_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        QUIZZES_PATH.parent.mkdir(parents=True, exist_ok=True)
        QUIZZES_PATH.write_text(
            json.dumps(all_quizzes, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"quiz state save failed: {e}", file=sys.stderr)

    # Award points if correct
    granted = 0
    if correct:
        rec = get_user(state, from_user["id"], display_name(from_user))
        granted = award_points(rec, QUIZ_REWARD)

    if correct:
        explain = quiz.get("explanation", "")
        # Truncate to fit 200-char alert limit
        msg = f"✅ Correct! +{granted} pts. {explain}"[:195]
        tg_answer_callback(token, cbid, msg, show_alert=True)
    else:
        msg = f"❌ Wrong — correct answer was {quiz['correct']}. Better luck tomorrow!"[:195]
        tg_answer_callback(token, cbid, msg, show_alert=True)


def process_updates(updates: list[dict], state: dict, token: str, start_offset: int) -> int:
    """Process a batch of updates. Returns new offset (max update_id + 1)."""
    new_offset = start_offset
    for upd in updates:
        new_offset = max(new_offset, upd.get("update_id", 0) + 1)

        # Inline-keyboard click on a quiz button
        cb = upd.get("callback_query")
        if cb:
            handle_quiz_callback(cb, state, token)
            continue

        msg = upd.get("message")
        if not msg:
            print(f"  upd {upd.get('update_id')}: not a message (keys={list(upd.keys())}) — skip")
            continue
        text = (msg.get("text") or "").strip()
        chat = msg.get("chat") or {}
        from_user = msg.get("from") or {}
        chat_summary = f"chat_id={chat.get('id')} type={chat.get('type')} from=@{from_user.get('username')}/{from_user.get('first_name')}"
        if not text.startswith("/"):
            print(f"  upd {upd.get('update_id')}: non-command text {text[:40]!r} ({chat_summary}) — skip")
            continue
        if not from_user or from_user.get("is_bot"):
            print(f"  upd {upd.get('update_id')}: bot/empty sender ({chat_summary}) — skip")
            continue
        if not chat:
            print(f"  upd {upd.get('update_id')}: no chat — skip")
            continue

        cmd, arg = route_command(text)
        if not cmd:
            print(f"  upd {upd.get('update_id')}: route returned empty — skip")
            continue
        print(f"  upd {upd.get('update_id')}: /{cmd} arg={arg!r} ({chat_summary})")

        rec = get_user(state, from_user["id"], display_name(from_user))

        # Per-command handlers + replies
        if cmd in ("start", "help"):
            reply = cmd_help()
        elif cmd == "news":
            reply = cmd_news()
        elif cmd == "blog":
            reply = cmd_blog()
        elif cmd == "price":
            reply = cmd_price(arg)
        elif cmd == "points":
            reply = cmd_points(rec)
        elif cmd == "leaderboard":
            reply = cmd_leaderboard(state)
        elif cmd == "ask":
            allowed, wait = can_use_ask(rec)
            if not allowed:
                reply = f"🤖 Cool down — try /ask again in {wait}s."
            else:
                reply = cmd_ask(arg)
                mark_ask(rec)
        elif cmd == "quiz":
            reply, was_correct = cmd_quiz(str(from_user["id"]), arg)
            if was_correct:
                # award the full quiz reward (subject to daily cap inside award_points)
                granted_quiz = award_points(rec, QUIZ_REWARD)
                if granted_quiz < QUIZ_REWARD:
                    reply = reply + f"\n\n<i>(daily cap reached — only +{granted_quiz} pts credited)</i>"
        else:
            # Unknown command — keep silent in groups to avoid noise,
            # respond with a hint in private chats.
            if chat.get("type") == "private":
                reply = f"Unknown command. Try /help."
            else:
                continue

        granted = award_points(rec, points_for_command(cmd))
        if granted > 0 and cmd in ("ask",):
            # Append a tiny pts hint for the ask path (visible reward signal).
            reply = reply + f"\n\n<i>+{granted} pts</i>"

        send_resp = tg_send(token, chat["id"], reply, reply_to=msg.get("message_id"))
        ok = bool(send_resp and send_resp.get("ok"))
        print(f"    -> sent={ok} ({len(reply)} chars, +{granted} pts)")
        if send_resp and not send_resp.get("ok"):
            print(f"    TG error: {send_resp}")

    return new_offset


def main() -> int:
    import time
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN missing — bot is offline. No-op.", file=sys.stderr)
        return 0

    state = load_state()
    offset = load_offset()
    deadline = time.monotonic() + LOOP_BUDGET_SEC
    print(f"Starting long-poll loop. offset={offset}, budget={LOOP_BUDGET_SEC}s.")

    iters = 0
    total_processed = 0
    while time.monotonic() < deadline:
        iters += 1
        updates = tg_get_updates(token, offset, timeout=LONG_POLL_TIMEOUT)
        if not updates:
            continue
        print(f"[iter {iters}] got {len(updates)} update(s) at offset={offset}")
        offset = process_updates(updates, state, token, offset)
        total_processed += len(updates)
        # Persist after each batch so a job kill mid-loop can't replay
        # already-answered commands.
        save_offset(offset)
        save_state(state)

    print(f"Loop done. iters={iters}, processed={total_processed}, final offset={offset}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
