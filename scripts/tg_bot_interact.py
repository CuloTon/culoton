"""Interactive Telegram bot for CuloTon community.

Polled every 2 minutes from .github/workflows/tg-interact.yml.

Reads pending updates via getUpdates with persistent offset
(data/tg_offset.txt), routes /commands, awards activity points
(data/points.json), and replies in English.

Commands:
  /start, /help        — welcome + command list
  /news                — latest 7 EN stories (near-dupe headlines collapsed)
  /blog                — link to the latest CuloScribe roundup
  /price ton|culoton   — live market data
  /ask <question>      — Haiku Q&A grounded in the latest 50 EN news
  /points              — caller's score
  /leaderboard         — top 10 most active members (running total)

Points: chatting in the group earns +1 (rate-limited to once per 90s),
/ask earns +3, other commands +1 — all capped at 20 points / user / UTC
day to prevent farming. Points accumulate continuously (no weekly reset);
rewards are discretionary. Every 10 group messages the bot posts a short
standings recap.
/ask is rate-limited to once every 3 minutes per user (paid API).
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from _culo_market import (
    CTAX_TAX,
    fetch_ctax_data,
    fetch_culo_data,
    fmt_change,
    fmt_money,
)
from _tg_points import (
    MSG_POINT_REWARD,
    award_points,
    can_earn_msg_point,
    can_use_ask,
    get_user,
    load_offset,
    load_state,
    mark_ask,
    mark_msg_point,
    save_offset,
    save_state,
    top_weekly,
)

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
BLOG_DIR = ROOT / "web" / "src" / "content" / "blog"
SITE = "https://culoton.fun"
RECAP_EVERY_N_MSGS = 10  # post a standings + rules recap every N group messages

TG_API_TIMEOUT = 35  # > long-poll timeout below, with margin
LONG_POLL_TIMEOUT = 25  # seconds; getUpdates returns immediately on new msg
GET_UPDATES_LIMIT = 100
LOOP_BUDGET_SEC = 270  # 4.5 minutes — leaves margin under workflow's 6-min cap
NEWS_FOR_LIST_MAX = 7        # /news always shows this many — newest first, no age cutoff
NEWS_RECENT_HOURS = 6        # only used for the "(N from the last Nh)" note in /news
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
    "/news — the 7 latest TON stories\n"
    "/blog — latest CuloScribe roundup\n\n"
    "💰 <b>Market</b>\n"
    "/price ton — live $TON price\n"
    "/price culoton — $CULOTON market data\n"
    "/price ctax — $CTAX market data (tax token: 25b/15s, 50% holders)\n\n"
    "🤖 <b>Ask me anything</b>\n"
    "/ask &lt;question&gt; — anything about TON, CuloTon, $CULOTON or sTONks; "
    f"light small-talk welcome too. <b>Limit: 1 per {ASK_COOLDOWN_MIN} min per user.</b>\n\n"
    "🏆 <b>Activity & rewards</b>\n"
    "💬 Every message in the group = +1 pt (max once per 90s). /ask = +3. Cap 20 pts/day.\n"
    "⚠️ Spamming to farm points = ban — post something worth reading.\n"
    "/points — your activity score\n"
    "/leaderboard — top 10 most active members (running total)\n"
    "🎁 Rewards are discretionary — the dev may reward standout active members "
    "from time to time. No fixed or guaranteed payout.\n\n"
    "🌐 <a href=\"https://culoton.fun\">culoton.fun</a>"
)


# ---------- Knowledge baked into /ask ---------------------------------------

CULOTON_FACTS = """\
CULO TON / $CULOTON — ground truth (always reply in English).

PLATFORM
- CuloTon (https://culoton.fun) is an English-language news desk covering the
  TON Blockchain ecosystem. It is the editorial layer built around the
  $CULOTON memecoin: legitimate TON content first, $CULOTON surfaced as the
  platform's native token (banner, /culo page, branding).
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

$CULOTON TOKEN
- Memecoin on TON. Contract: EQAYaqIikryTucQEz3IGRC62M7Eo4rzvduFAV5iWZ1b0A2Uc
- Track record: ~10,000X market-cap move on Polygon (2024), follow-through on
  SUI, then launched on TON in 2026 with this dedicated platform.
- Relaunched in May 2026 as a tax-free token under the new ticker $CULOTON,
  retiring the original $CULO contract. The relaunch was triggered by
  consultations with senior figures in the TON ecosystem who endorsed the
  project as developmental but required a token without TAX.
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

$CULOTON RELATION
- $CULOTON is the live token of the project (TON contract
  EQAYaqIikryTucQEz3IGRC62M7Eo4rzvduFAV5iWZ1b0A2Uc, tax-free). It is the
  relaunched successor to the original $CULO contract, which was deployed via
  stonks.pump and has since been retired. The CuloTon news desk is the
  editorial layer that the token sits inside.
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


# Words too generic to count toward "two headlines are the same story".
_TITLE_STOPWORDS = frozenset({
    "a", "an", "the", "on", "in", "of", "to", "for", "and", "as", "at",
    "with", "by", "amid", "this", "that", "from", "is", "are", "be", "its",
    "it", "after", "over", "into", "than", "but", "or", "up", "down", "out",
})


def _title_tokens(title: str) -> frozenset[str]:
    """Normalised content words of a headline (lowercased, depluralised,
    stopwords dropped) — the basis for near-duplicate detection."""
    out: set[str] = set()
    for tok in re.split(r"[^0-9a-z]+", (title or "").lower()):
        if not tok or tok in _TITLE_STOPWORDS:
            continue
        if len(tok) > 3 and tok.endswith("s"):
            tok = tok[:-1]
        out.add(tok)
    return frozenset(out)


def _near_duplicate_titles(a: frozenset[str], b: frozenset[str], threshold: float = 0.6) -> bool:
    if not a or not b:
        return False
    return len(a & b) / min(len(a), len(b)) >= threshold


def dedup_news(items: list[dict], limit: int | None = None) -> list[dict]:
    """Collapse near-identical headlines (the same story re-reported by several
    outlets) — keeps the first occurrence, so pass items newest-first.
    Stops early once `limit` survivors have been collected."""
    kept: list[dict] = []
    seen: list[frozenset[str]] = []
    for it in items:
        toks = _title_tokens(it.get("title", ""))
        if any(_near_duplicate_titles(toks, prev) for prev in seen):
            continue
        kept.append(it)
        seen.append(toks)
        if limit is not None and len(kept) >= limit:
            break
    return kept


def latest_news(n: int) -> list[dict]:
    """Up to `n` most recent EN stories, newest first, near-duplicate
    headlines collapsed. No age cutoff — always returns what exists."""
    en = NEWS_DIR / "en"
    if not en.exists():
        return []
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
            "source_name": (fm.get("source_name") or "").strip(),
            "tags": fm.get("tags") or [],
            "date": dt,
        }))
    items.sort(key=lambda x: x[0], reverse=True)
    return dedup_news([it[1] for it in items], limit=n)


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
    items = latest_news(NEWS_FOR_LIST_MAX)
    if not items:
        return "📰 No news yet. Check back soon — new stories drop through the day."
    cutoff = datetime.now(timezone.utc) - timedelta(hours=NEWS_RECENT_HOURS)
    recent = sum(1 for it in items if it.get("date") and it["date"] >= cutoff)
    header = f"📰 <b>Latest {len(items)} stories</b>"
    if recent:
        header += f" — <i>{recent} from the last {NEWS_RECENT_HOURS}h</i>"
    lines = [header + "\n"]
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
    if asset in ("culo", "$culo", "culoton", "$culoton"):
        d = fetch_culo_data()
        if not d or d.get("price") is None:
            return "💰 $CULOTON market data unavailable right now. Try again in a minute."
        price = fmt_money(d["price"])
        change = fmt_change(d.get("change_h24"))
        vol = fmt_money(d.get("vol_h24"))
        valuation = fmt_money(d.get("valuation"))
        return (
            "💰 <b>$CULOTON — live</b>\n\n"
            f"Price: <b>{price}</b> ({change} 24h)\n"
            f"FDV: {valuation}\n"
            f"24h volume: {vol}\n\n"
            "Source: GeckoTerminal"
        )
    if asset in ("ctax", "$ctax", "culotax", "$culotax"):
        d = fetch_ctax_data()
        tax_line = (
            f"Tax: <b>{CTAX_TAX['buy']}%</b> buy · <b>{CTAX_TAX['sell']}%</b> sell · "
            f"<b>{CTAX_TAX['holders_share']}%</b> of tax → holders"
        )
        if not d or d.get("price") is None:
            return (
                "💰 <b>$CTAX — companion tax token</b>\n\n"
                f"{tax_line}\n\n"
                "No DEX market data yet — token is freshly deployed, "
                "ownership already renounced (admin = 0x0). Live price will appear "
                "here as soon as a pool exists on GeckoTerminal."
            )
        price = fmt_money(d["price"])
        change = fmt_change(d.get("change_h24"))
        vol = fmt_money(d.get("vol_h24"))
        valuation = fmt_money(d.get("valuation"))
        return (
            "💰 <b>$CTAX — live</b>\n\n"
            f"Price: <b>{price}</b> ({change} 24h)\n"
            f"FDV: {valuation}\n"
            f"24h volume: {vol}\n\n"
            f"{tax_line}\n\n"
            "Source: GeckoTerminal"
        )
    return "Usage: /price ton  ·  /price culoton  ·  /price ctax"


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
        "- Anything about CuloTon, the $CULOTON token, this Telegram bot, the news "
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


def cmd_points(rec: dict) -> str:
    name = html.escape(rec.get("username") or "you")
    return (
        f"🏆 <b>{name}</b>\n\n"
        f"Activity points: <b>{rec.get('total_points', 0)}</b>\n"
        f"Today (cap 20): {rec.get('daily_points', 0)} pts\n\n"
        f"Use /leaderboard to see how you stack up."
    )


def cmd_leaderboard(state: dict) -> str:
    top = top_weekly(state, n=10)
    if not top:
        return (
            "🏆 <b>Leaderboard — most active members</b>\n\n"
            "Nobody has earned points yet — "
            "be first. Try /news, /price ton, or /ask &lt;question&gt;."
        )
    lines = ["🏆 <b>Leaderboard — top 10 most active</b>\n"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (_uid, rec) in enumerate(top):
        pos = medals[i] if i < 3 else f"{i+1}."
        name = html.escape(rec.get("username") or "anon")
        pts = rec.get("weekly_points", 0)
        lines.append(f"{pos} <b>{name}</b> — {pts} pts")
    lines.append(
        "\n🎁 Rewards are discretionary — the dev may reward standout active members "
        "from time to time. No fixed or guaranteed payout."
    )
    return "\n".join(lines)


_RULES_FOOTER = (
    "🎯 <b>How to score:</b> every message in this group = +1 pt (rate-limited) · "
    "/ask = +3. Cap 20 pts/day per person. Spamming to farm points = ban — post something worth reading.\n"
    "🎁 Rewards are discretionary — the dev may reward standout active members from time to time. "
    "No fixed payout. /leaderboard · /points"
)


def build_standings_recap(state: dict) -> str:
    """Short standings + contest rules — posted every RECAP_EVERY_N_MSGS group messages."""
    top = top_weekly(state, n=5)
    if not top:
        head = "📊 <b>CULO COMMUNITY — activity standings</b>\n\nNo scores yet — be first. Just chat here, use /ask or /news."
    else:
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        rows = ["📊 <b>CULO COMMUNITY — activity standings</b>", ""]
        for i, (_uid, rec) in enumerate(top, 1):
            name = (rec.get("username") or "anon").strip()
            if name and not name.startswith("@") and " " not in name:
                name = "@" + name
            rows.append(f"{medals.get(i, f'{i}.')} {html.escape(name)} — <b>{rec.get('weekly_points', 0)}</b> pts")
        head = "\n".join(rows)
    return head + "\n\n" + _RULES_FOOTER


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


def process_updates(updates: list[dict], state: dict, token: str, start_offset: int) -> int:
    """Process a batch of updates. Returns new offset (max update_id + 1)."""
    new_offset = start_offset
    state.setdefault("group_msg_count", 0)
    msg_count_before = state["group_msg_count"]
    last_group_chat_id = None
    for upd in updates:
        new_offset = max(new_offset, upd.get("update_id", 0) + 1)

        # Quiz retired — ignore any stray inline-keyboard callbacks.
        if upd.get("callback_query"):
            continue

        msg = upd.get("message")
        if not msg:
            print(f"  upd {upd.get('update_id')}: not a message (keys={list(upd.keys())}) — skip")
            continue
        text = (msg.get("text") or "").strip()
        chat = msg.get("chat") or {}
        from_user = msg.get("from") or {}
        chat_type = chat.get("type")
        chat_summary = f"chat_id={chat.get('id')} type={chat_type} from=@{from_user.get('username')}/{from_user.get('first_name')}"

        if not from_user or from_user.get("is_bot") or not chat:
            print(f"  upd {upd.get('update_id')}: bot/empty sender or no chat ({chat_summary}) — skip")
            continue

        # Plain (non-command) message in a group → small activity point, rate-limited,
        # and counts toward the periodic standings recap. No reply.
        if not text.startswith("/"):
            if chat_type in ("group", "supergroup"):
                state["group_msg_count"] = state.get("group_msg_count", 0) + 1
                last_group_chat_id = chat.get("id")
                rec = get_user(state, from_user["id"], display_name(from_user))
                ok_msg, _wait = can_earn_msg_point(rec)
                if ok_msg:
                    g = award_points(rec, MSG_POINT_REWARD)
                    mark_msg_point(rec)
                    print(f"  upd {upd.get('update_id')}: chat msg ({chat_summary}) -> +{g} pt (week={rec.get('weekly_points', 0)})")
                else:
                    print(f"  upd {upd.get('update_id')}: chat msg ({chat_summary}) -> cooldown, no pt")
            else:
                print(f"  upd {upd.get('update_id')}: non-command text in {chat_type} ({chat_summary}) — skip")
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

    # Every RECAP_EVERY_N_MSGS group messages, post a short standings + rules
    # recap. At most once per batch even if a burst crossed several thresholds.
    after = state.get("group_msg_count", 0)
    if after > msg_count_before and (after // RECAP_EVERY_N_MSGS) > (msg_count_before // RECAP_EVERY_N_MSGS):
        recap_chat = last_group_chat_id or (os.environ.get("TELEGRAM_CHAT_ID") or "").strip() or None
        if recap_chat:
            recap = build_standings_recap(state)
            r = tg_send(token, recap_chat, recap)
            print(f"  standings recap posted to {recap_chat} at msg #{after}: ok={bool(r and r.get('ok'))}")

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
