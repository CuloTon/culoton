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

TG_API_TIMEOUT = 25
GET_UPDATES_LIMIT = 100
NEWS_FOR_LIST_HOURS = 6
NEWS_FOR_LIST_MAX = 5
ASK_CONTEXT_NEWS_COUNT = 50
ASK_MAX_QUESTION_CHARS = 400

ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

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
    "/ask &lt;question&gt; — I'll answer using the latest TON news as context\n\n"
    "🏆 <b>Activity & rewards</b>\n"
    "/points — your activity score\n"
    "/leaderboard — top 10 most active members this week\n"
    "ℹ The top 3 active members each week get rewards "
    "(announced every Sunday).\n\n"
    "🌐 <a href=\"https://culoton.fun\">culoton.fun</a>"
)


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


def tg_get_updates(token: str, offset: int) -> list[dict]:
    payload = {
        "offset": offset,
        "limit": GET_UPDATES_LIMIT,
        "timeout": 0,
        "allowed_updates": json.dumps(["message"]),
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
        "You are CuloScribe, the AI editor of CuloTon — a TON-blockchain news desk. "
        "Answer the user's question using the news context below as your primary "
        "source of facts. Be concise (2-4 short paragraphs max), confident, and "
        "in plain English. If the context does not cover the question, say so "
        "and answer from general TON-ecosystem knowledge, marking it clearly. "
        "Do not invent prices, dates, or quotes that are not in the context. "
        "Never recommend buying or selling. End with one short editorial take."
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
        f"{html.escape(answer)}"
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
        "\n🎁 Top 3 each week receive prizes — winners announced every Sunday at 20:00 UTC."
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


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN missing — bot is offline. No-op.", file=sys.stderr)
        return 0

    offset = load_offset()
    updates = tg_get_updates(token, offset)
    if not updates:
        print("No new updates.")
        return 0
    print(f"Got {len(updates)} update(s). Starting offset={offset}.")

    state = load_state()
    new_offset = offset

    for upd in updates:
        new_offset = max(new_offset, upd.get("update_id", 0) + 1)
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

    save_state(state)
    save_offset(new_offset)
    print(f"Done. New offset={new_offset}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
