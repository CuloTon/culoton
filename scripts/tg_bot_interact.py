"""Interactive Telegram bot for BRAINROT community.

Polled every 2 minutes from .github/workflows/tg-interact.yml.

Reads pending updates via getUpdates with persistent offset
(data/tg_offset.txt), routes /commands, awards activity points
(data/points.json), and replies in English.

Commands:
  /start, /help        — welcome + command list
  /news                — latest 7 EN stories (near-dupe headlines collapsed)
  /blog                — link to the latest BrainScribe roundup
  /price ton|brt       — live market data
  /roll                — TON rewards paid to date + rollover status
  /simulate            — projected payouts at 25/50/100/500 TON (current holders)
  /points              — caller's score
  /leaderboard         — top 10 most active members (running total)

Points: chatting in the group earns +1 (rate-limited to once per 90s),
commands +1 — all capped at 20 points / user / UTC day to prevent farming.
Points accumulate continuously (no weekly reset); rewards are discretionary.
Every 10 group messages the bot posts a short standings recap.

/roll is GLOBAL-rate-limited to once every 10 minutes (one call locks it for
everyone) — except the dev/admin, who has no limit.
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
    fetch_culo_data,
    fmt_change,
    fmt_money,
)
from _tg_points import (
    MSG_POINT_REWARD,
    ROLL_COOLDOWN_SEC,
    award_points,
    can_earn_msg_point,
    can_use_roll,
    get_user,
    load_offset,
    load_state,
    mark_msg_point,
    mark_roll,
    save_offset,
    save_state,
    top_weekly,
)

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
BLOG_DIR = ROOT / "web" / "src" / "content" / "blog"
REWARDS_DATA = ROOT / "web" / "src" / "data" / "rewards_rounds.json"
SIMULATION_DATA = ROOT / "web" / "src" / "data" / "rewards_simulation.json"
SITE = "https://brainrot-ton.fun"

# Reward bank wallet (mirrors scripts/rewards_snapshot.py / RewardsContent.astro).
DEV_ADDRESS = "UQBzaZXIwj3mDY8HdYDkTO1lkn4OV8sfx2tsf-lChQex70NP"
REWARD_PCT = 0.25
ROLL_COOLDOWN_MIN = ROLL_COOLDOWN_SEC // 60

# Admin/dev usernames that bypass the global /roll cooldown. Telegram usernames
# are unique and non-transferable, so this is a safe (if simple) admin check.
# Override via env TELEGRAM_ADMIN_USERNAMES="name1,name2" (no @).
DEV_USERNAMES = {
    u.strip().lstrip("@").lower()
    for u in (os.environ.get("TELEGRAM_ADMIN_USERNAMES") or "culodaddy_ton").split(",")
    if u.strip()
}
RECAP_EVERY_N_MSGS = 10  # post a standings + rules recap every N group messages

TG_API_TIMEOUT = 35  # > long-poll timeout below, with margin
LONG_POLL_TIMEOUT = 25  # seconds; getUpdates returns immediately on new msg
GET_UPDATES_LIMIT = 100
LOOP_BUDGET_SEC = 270  # 4.5 minutes — leaves margin under workflow's 6-min cap
NEWS_FOR_LIST_MAX = 7        # /news always shows this many — newest first, no age cutoff
NEWS_RECENT_HOURS = 6        # only used for the "(N from the last Nh)" note in /news

COMMANDS_HELP = (
    "👋 <b>Welcome to BRAINROT Desk</b>\n"
    "I'm <b>@brainrot_info_bot</b> — the editorial AI for BRAINROT, "
    "covering the TON ecosystem 24/7.\n\n"
    "📰 <b>News</b>\n"
    "/news — the 7 latest TON stories\n"
    "/blog — latest BrainScribe roundup\n\n"
    "💰 <b>Market</b>\n"
    "/price ton — live $TON price\n"
    "/price brt — $BRT market data\n\n"
    "🎁 <b>Rewards</b>\n"
    "/roll — TON rewards paid to date + rollover status\n"
    "/simulate — projected payouts at 25 / 50 / 100 / 500 TON (current holders)\n\n"
    "🏆 <b>Activity & rewards</b>\n"
    "💬 Every message in the group = +1 pt (max once per 90s). Cap 20 pts/day.\n"
    "⚠️ Spamming to farm points = ban — post something worth reading.\n"
    "/points — your activity score\n"
    "/leaderboard — top 10 most active members (running total)\n"
    "🎁 Rewards are discretionary — the dev may reward standout active members "
    "from time to time. No fixed or guaranteed payout.\n\n"
    "🌐 <a href=\"https://brainrot-ton.fun\">brainrot-ton.fun</a>"
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


def tg_send(token: str, chat_id: int | str, text: str, *, reply_to: int | None = None, reply_markup: dict | None = None) -> dict | None:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
        payload["allow_sending_without_reply"] = "true"
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
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
        req = urllib.request.Request(url, headers={"User-Agent": "BRAINROT-Bot/1.0"})
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
        return "📓 No blog roundup yet. BrainScribe drops them 3× daily."
    url = f"{SITE}/blog/{blog['slug']}/"
    title = html.escape(blog["title"])
    summary = html.escape(blog["summary"])
    kind_emoji = {"morning": "⚡", "noon": "☀️", "evening": "🌅"}.get(blog.get("kind", ""), "📓")
    kind = (blog.get("kind") or "").upper() or "ROUNDUP"
    return (
        f"{kind_emoji} <b>BrainScribe — {kind}</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"{summary}\n\n"
        f"👉 <a href=\"{url}\">Read on brainrot-ton.fun</a>"
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
    if asset in ("brt", "$brt", "brainrot", "$brainrot", "culo", "$culo", "culoton", "$culoton"):
        d = fetch_culo_data()
        if not d or d.get("price") is None:
            return "💰 $BRT market data unavailable right now. Try again in a minute."
        price = fmt_money(d["price"])
        change = fmt_change(d.get("change_h24"))
        vol = fmt_money(d.get("vol_h24"))
        valuation = fmt_money(d.get("valuation"))
        return (
            "💰 <b>$BRT — live</b>\n\n"
            f"Price: <b>{price}</b> ({change} 24h)\n"
            f"FDV: {valuation}\n"
            f"24h volume: {vol}\n\n"
            "Source: GeckoTerminal"
        )
    return "Usage: /price ton  ·  /price brt"


def is_admin(from_user: dict) -> bool:
    """Dev/admin bypasses the /roll cooldown. Matched on Telegram username
    (unique, non-transferable) against DEV_USERNAMES."""
    uname = (from_user.get("username") or "").strip().lstrip("@").lower()
    return bool(uname) and uname in DEV_USERNAMES


def fetch_bank_ton() -> float | None:
    """Live reward-bank (DEV wallet) TON balance via tonapi. Read-only."""
    url = f"https://tonapi.io/v2/accounts/{DEV_ADDRESS}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=TG_API_TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
        return int(data.get("balance", 0)) / 1e9
    except Exception as e:
        print(f"  bank balance fetch failed: {e}", file=sys.stderr)
        return None


def load_rewards_rounds() -> dict:
    """Consolidated payout history, written by
    brt-nagrody/scripts/export_rounds_to_site.py. Same file the website reads."""
    try:
        return json.loads(REWARDS_DATA.read_text(encoding="utf-8"))
    except Exception:
        return {}


def cmd_roll() -> str:
    data = load_rewards_rounds()
    rounds = data.get("rounds", [])
    total_paid = float(data.get("total_paid_ton", 0) or 0)
    n_rounds = data.get("rounds_count", len(rounds))

    lines = ["💸 <b>$BRT rewards — rollover status</b>\n"]

    bank = fetch_bank_ton()
    if bank is not None:
        all_pool = bank * REWARD_PCT
        top_pool = bank * REWARD_PCT
        lines.append(f"🏦 Reward bank now: <b>{bank:.2f} TON</b>")
        lines.append(f"   • All-holders pool (25%): ~{all_pool:.3f} TON")
        lines.append(f"   • TOP-10 pool (25%): ~{top_pool:.3f} TON ★ — top 10 get this <b>on top</b>")
        lines.append(f"   → holders share ~{all_pool + top_pool:.3f} TON total (50%)")

    if rounds:
        lines.append(f"✅ Paid to date: <b>{total_paid:.3f} TON</b> across "
                     f"{n_rounds} round{'s' if n_rounds != 1 else ''}")
        last = rounds[-1]
        lines.append(f"🏅 Last round #{last.get('round')} ({(last.get('at') or '')[:10]}): "
                     f"{len(last.get('paid', []))} holders, {float(last.get('total_paid_ton', 0)):.3f} TON")
        roll = last.get("rollover", [])
        if roll:
            roll_sum = sum(float(h.get("ton", 0)) for h in roll)
            lines.append(f"⏳ Rolling over: {len(roll)} wallets ({roll_sum:.3f} TON) — "
                         "shares below 0.05 TON. Not a stored credit: every round is "
                         "recomputed from your live $BRT balance — keep holding and it "
                         "crosses 0.05; sell and there's nothing left to roll.")
    else:
        lines.append("No rounds have paid out yet — the first runs once the bank passes 4 TON.")

    lines.append(f"\n📊 Full breakdown, ranked & on-chain ↗ <a href=\"{SITE}/rewards\">{SITE}/rewards</a>")
    lines.append("🔮 Curious what bigger banks pay? Try /simulate")
    return "\n".join(lines)


def load_simulation() -> dict:
    """Pre-computed payout projection written by
    brt-nagrody/scripts/rewards_snapshot.py (build_simulation). Based on the
    holder distribution at the time the snapshot ran."""
    try:
        return json.loads(SIMULATION_DATA.read_text(encoding="utf-8"))
    except Exception:
        return {}


def cmd_simulate() -> str:
    sim = load_simulation()
    levels = sim.get("levels", [])
    if not levels:
        return ("🔮 No simulation available yet — it's generated from the current "
                "holder snapshot. Check back shortly, or see "
                f"<a href=\"{SITE}/rewards\">{SITE}/rewards</a>.")

    when = (sim.get("generated_at") or "")[:10]
    n = sim.get("n_eligible", 0)
    lines = [
        "🔮 <b>$BRT reward simulation</b>",
        f"<i>Based on the current {n} eligible holders"
        f"{f' (snapshot {when})' if when else ''} — every number shifts as balances change.</i>",
        "",
        "Model: <b>25% to ALL holders + 25% to the TOP 10</b>, both pro-rata. "
        "The TOP 10 (★) are paid from <b>both</b> pools — so they earn far more than 25% alone.",
    ]
    for lv in levels:
        bank = lv.get("bank", 0)
        all_p = lv.get("all_pool_ton", 0)
        top_p = lv.get("top10_pool_ton", 0)
        top = lv.get("top", [])
        lines.append("")
        lines.append(f"💰 <b>Bank {bank:.0f} TON</b> → holders {all_p + top_p:.2f} TON "
                     f"(all {all_p:.2f} + top10 {top_p:.2f})")
        # #1 (biggest, top 10) and a mid-pack holder to show the gap.
        if top:
            r1 = top[0]
            lines.append(f"   🥇 #1 ({r1.get('pct', 0):.1f}% supply) ★ → <b>{r1.get('ton', 0):.3f} TON</b> "
                         f"(all {r1.get('ton_all', 0):.3f} + top10 {r1.get('ton_top10', 0):.3f})")
            if len(top) >= 10:
                r10 = top[9]
                lines.append(f"   #10 ({r10.get('pct', 0):.1f}% supply) ★ → {r10.get('ton', 0):.3f} TON")
    lines.append("")
    lines.append(f"📊 Live bank & full ranking ↗ <a href=\"{SITE}/rewards\">{SITE}/rewards</a>")
    return "\n".join(lines)


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
            "be first. Try /news, /price ton, or /roll."
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
    "🎯 <b>How to score:</b> every message in this group = +1 pt (rate-limited). "
    "Cap 20 pts/day per person. Spamming to farm points = ban — post something worth reading.\n"
    "🎁 Rewards are discretionary — the dev may reward standout active members from time to time. "
    "No fixed payout. /leaderboard · /points"
)


def build_standings_recap(state: dict) -> str:
    """Short standings + contest rules — posted every RECAP_EVERY_N_MSGS group messages."""
    top = top_weekly(state, n=5)
    if not top:
        head = "📊 <b>CULO COMMUNITY — activity standings</b>\n\nNo scores yet — be first. Just chat here, use /news or /roll."
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
    if cmd in ("start", "help", "news", "blog", "price", "roll", "simulate", "sim", "points", "leaderboard"):
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
        markup = None
        if cmd in ("start", "help"):
            reply = cmd_help()
        elif cmd == "news":
            reply = cmd_news()
        elif cmd == "blog":
            reply = cmd_blog()
        elif cmd == "price":
            reply = cmd_price(arg)
        elif cmd == "roll":
            if is_admin(from_user):
                reply = cmd_roll()
            else:
                allowed, wait = can_use_roll(state)
                if not allowed:
                    m, s = divmod(wait, 60)
                    reply = (f"⏳ /roll is on a shared {ROLL_COOLDOWN_MIN}-minute cooldown "
                             f"(one call locks it for everyone). Try again in {m}m {s:02d}s.")
                else:
                    reply = cmd_roll()
                    mark_roll(state)
        elif cmd in ("simulate", "sim"):
            reply = cmd_simulate()
        elif cmd == "points":
            reply = cmd_points(rec)
        elif cmd == "leaderboard":
            reply = cmd_leaderboard(state)
        elif cmd in ("tax", "app", "tokens"):
            reply = "📊 <b>BRAINROT TAX board</b> — live TON token charts, market cap and buy/sell/holders tax."
            if chat.get("type") == "private":
                markup = {"inline_keyboard": [[{"text": "📊 Open TAX board", "web_app": {"url": SITE + "/app"}}]]}
            else:
                # web_app inline buttons aren't allowed in groups → use the
                # direct-link Mini App (t.me/<bot>/<shortname>), which opens
                # the Mini App in-Telegram from any chat. Requires the Mini App
                # to be registered in BotFather (short name: tax).
                markup = {"inline_keyboard": [[{"text": "📊 Open TAX board", "url": "https://t.me/brainrot_info_bot/tax"}]]}
        else:
            # Unknown command — keep silent in groups to avoid noise,
            # respond with a hint in private chats.
            if chat.get("type") == "private":
                reply = f"Unknown command. Try /help."
            else:
                continue

        granted = award_points(rec, points_for_command(cmd))

        send_resp = tg_send(token, chat["id"], reply, reply_to=msg.get("message_id"), reply_markup=markup)
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
