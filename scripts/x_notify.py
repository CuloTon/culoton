"""CuloTon X (Twitter) notifier.

Three modes (--mode news/fomo/mcap), each can run in TWO delivery modes:

  • LIVE mode (default when X_DRAFTS_CHAT_ID is NOT set): uses tweepy
    OAuth 1.0a to POST /2/tweets directly. Requires Basic tier
    ($100/month) — Free tier returns 402.

  • DRAFT mode (active when X_DRAFTS_CHAT_ID is set): does NOT call
    the X API at all. Builds the tweet text, then sends it to a
    private Telegram chat with the bot together with a one-tap
    "Open in X" deep link (https://twitter.com/intent/tweet?text=…).
    User taps the link → X compose opens with the tweet pre-filled
    → user taps Post. $0 / month, ~5 seconds of manual work per
    post. Dedup still works (news_drafted state), so the same news
    is not drafted twice.

Graceful no-ops when neither delivery path is configured.
"""

from __future__ import annotations

import argparse
import html
import os
import random
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    import tweepy
except ImportError:
    tweepy = None  # graceful no-op when dep missing

from _culo_market import (  # noqa: E402
    CTAX_TAX,
    fetch_ctax_data,
    fetch_culo_data,
    fmt_change,
    fmt_money,
)

# tg_send is reused from telegram_notify so we don't duplicate the
# Telegram HTTP wiring. Imported lazily inside draft path so the X
# script still works in live mode without telegram secrets.

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
DB_PATH = Path(__file__).resolve().parent / "x_announced.db"

SITE = "https://culoton.fun"
URL_LEN = 23   # X shortens every URL through t.co; counts as 23 chars
TWEET_MAX = 280

# Hashtag policy (avoid spam flagging):
#  - 2 fixed core tags so the brand is consistent across every tweet
#  - 1-2 randomly picked from a niche pool (rotates → no duplicate-content flag)
#  - For news mode, also 1 article-specific tag if available in frontmatter
#  - Hard cap at ~4 hashtags total — X starts treating 5+ as spam
CORE_TAGS = ["#TON", "#CULOTON"]

NICHE_POOL = [
    "#CULO",
    "#Toncoin",
    "#TONblockchain",
    "#TONecosystem",
    "#memecoin",
    "#memecoins",
    "#CryptoNews",
    "#Web3",
    "#DeFi",
    "#TONcommunity",
    "#cryptotwitter",
    "#altcoin",
    "#blockchain",
    "#crypto",
]

FOMO_LINES = [
    "TON is quietly eating 2026. CuloTon publishes the receipts. $CULOTON is along for the ride.",
    "Three previous chains, one narrative. $CULOTON came home — and home is on TON.",
    "We don't shill TON. We publish three roundups a day about it. Coincidence? No. $CULOTON",
    "Telegram is the chat. TON is the chain. $CULOTON is the meme that ties them.",
    "Sub-second blocks on TON. Sub-280-character takes from CuloTon. $CULOTON is the punchline.",
    "Most projects shill. CuloTon publishes. Then we mention $CULOTON — lightly.",
    "If TON wins, $CULOTON wins. Track record: 10,000X on Polygon, then SUI, now TON.",
    "Small cap. Big chain. Attentive crew. $CULOTON on TON — and we're just clearing our throat.",
    "Don't bet on TON. Be on it. $CULOTON is one of many ways.",
    "Build the media voice first, the bag follows. CuloTon → $CULOTON → TON. In that order.",
    "While altcoins fight for relevance, TON ships and CuloTon writes it down. $CULOTON funds the desk.",
    "The fastest chain in crypto runs the most-used messenger on Earth. $CULOTON is the meme leg.",
]

# Short tags appended to the live mcap pulse — bullish, brief.
MCAP_TAGLINES = [
    "Don't sleep on this one.",
    "Memecoins on the fastest chain in crypto.",
    "The TON ecosystem leg of $CULOTON.",
    "Native to TON. Loud about it.",
    "Built different. Priced like a meme. For now.",
    "We're early. You're not too late.",
    "Small cap energy on the chain Telegram bets on.",
]


def get_delivery_mode() -> str:
    """Returns 'draft', 'live' or 'noop' depending on which secrets are present.

    DRAFT wins over LIVE when both could work — that's the cheap path,
    and X live currently needs paid tier anyway.
    """
    drafts_chat = (os.getenv("X_DRAFTS_CHAT_ID") or "").strip()
    tg_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if drafts_chat and tg_token:
        return "draft"
    ck = (os.getenv("X_CONSUMER_KEY") or "").strip()
    cs = (os.getenv("X_CONSUMER_SECRET") or "").strip()
    at = (os.getenv("X_ACCESS_TOKEN") or "").strip()
    ats = (os.getenv("X_ACCESS_TOKEN_SECRET") or "").strip()
    if all([ck, cs, at, ats]) and tweepy is not None:
        return "live"
    return "noop"


def get_client():
    ck = (os.getenv("X_CONSUMER_KEY") or "").strip()
    cs = (os.getenv("X_CONSUMER_SECRET") or "").strip()
    at = (os.getenv("X_ACCESS_TOKEN") or "").strip()
    ats = (os.getenv("X_ACCESS_TOKEN_SECRET") or "").strip()
    if not all([ck, cs, at, ats]) or tweepy is None:
        return None
    return tweepy.Client(
        consumer_key=ck,
        consumer_secret=cs,
        access_token=at,
        access_token_secret=ats,
    )


def send_draft_to_telegram(*, kind_label: str, tweet_text: str, char_total: int) -> int:
    """Posts the tweet text to the private TG drafts chat with a one-tap
    'Open in X compose' link. Returns 0/1 like the rest of the post_* helpers.
    """
    from telegram_notify import tg_send  # local import — only needed for draft path

    tg_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    drafts_chat = (os.getenv("X_DRAFTS_CHAT_ID") or "").strip()
    if not tg_token or not drafts_chat:
        print("draft mode missing TELEGRAM_BOT_TOKEN or X_DRAFTS_CHAT_ID", file=sys.stderr)
        return 1

    intent_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(tweet_text, safe="")

    body = (
        f"📝 <b>X DRAFT — {html.escape(kind_label)}</b>  ({char_total}/280)\n\n"
        f"<pre>{html.escape(tweet_text)}</pre>\n\n"
        f"→ <a href=\"{intent_url}\">Open in X (1 tap to post)</a>"
    )
    status, resp_body = tg_send(tg_token, drafts_chat, body, disable_preview=True)
    if status != 200:
        print(f"draft post to TG failed: status={status} body={resp_body}", file=sys.stderr)
        return 1
    # Surface non-secret identity fields from the TG echo so the run log
    # makes it obvious WHICH chat received the draft. The numeric chat.id
    # equals the X_DRAFTS_CHAT_ID secret and gets masked by gh as ***,
    # but chat.type / chat.first_name / chat.title are not redacted.
    chat_tail = drafts_chat[-4:] if len(drafts_chat) >= 4 else drafts_chat
    chat_descr = "?"
    try:
        import json as _json
        echo = _json.loads(resp_body)
        chat = (echo.get("result") or {}).get("chat") or {}
        ctype = chat.get("type", "?")
        cname = chat.get("first_name") or chat.get("title") or chat.get("username") or "?"
        cmid = (echo.get("result") or {}).get("message_id", "?")
        chat_descr = f"type={ctype} name={cname!r} msg_id={cmid}"
    except Exception as e:  # noqa: BLE001
        chat_descr = f"parse_err={e!r}"
    print(
        f"draft sent to TG ({kind_label}, {char_total}/280, "
        f"chat_id_tail=...{chat_tail}, {chat_descr})"
    )
    return 0


def url_is_live(url: str, timeout: float = 5.0) -> bool:
    """HEAD-check the article URL before announcing. Guards against the
    race where update-and-deploy committed the file but FTP upload
    hasn't finished — without this we'd post a draft pointing to a 404.
    """
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "culoton-bot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(f"url_is_live({url!r}) failed: {type(e).__name__}: {e}", file=sys.stderr)
        return False


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    if not md_text.startswith("---"):
        return {}, md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}, md_text
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].lstrip("\n")


def db_init() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS announced (
            slug TEXT NOT NULL,
            kind TEXT NOT NULL,
            announced_at TEXT NOT NULL,
            PRIMARY KEY (slug, kind)
        )"""
    )
    conn.commit()
    return conn


def already_announced(conn, slug, kind):
    return conn.execute("SELECT 1 FROM announced WHERE slug=? AND kind=?", (slug, kind)).fetchone() is not None


def mark_announced(conn, slug, kind):
    conn.execute(
        "INSERT OR IGNORE INTO announced (slug, kind, announced_at) VALUES (?,?,?)",
        (slug, kind, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def find_next_news(conn):
    en_dir = NEWS_DIR / "en"
    if not en_dir.exists():
        return None
    cands = []
    for p in en_dir.glob("*.md"):
        slug = p.stem
        if already_announced(conn, slug, "news"):
            continue
        try:
            fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if fm.get("date") and fm.get("title"):
            cands.append((slug, fm))
    cands.sort(key=lambda x: str(x[1].get("date", "")), reverse=True)
    return cands[0] if cands else None


def char_count(text: str) -> int:
    """Approximate X tweet length: URLs count as URL_LEN regardless of actual length."""
    parts = re.split(r"(https?://\S+)", text)
    total = 0
    for p in parts:
        total += URL_LEN if p.startswith("http") else len(p)
    return total


def slugify_hashtag(tag: str) -> str | None:
    cleaned = "".join(c for c in tag if c.isalnum())
    return "#" + cleaned if cleaned else None


def pick_hashtags(article_tags: list[str] | None = None, *, niche_count: int = 2) -> str:
    chosen = list(CORE_TAGS)
    seen = {t.lower() for t in chosen}
    pool = [t for t in NICHE_POOL if t.lower() not in seen]
    random.shuffle(pool)
    for t in pool[:niche_count]:
        chosen.append(t)
        seen.add(t.lower())
    if article_tags:
        for t in article_tags:
            ht = slugify_hashtag(t)
            if ht and ht.lower() not in seen and len(ht) > 2:
                chosen.append(ht)
                break
    return " ".join(chosen)


def build_news_tweet(title: str, summary: str, tags: list[str], url: str) -> str:
    hashtags = pick_hashtags(article_tags=tags, niche_count=1)  # 2 core + 1 niche + 1 article = 4 total max

    candidate = f"{title}\n\n{summary}\n\n{hashtags}\n\n{url}"
    if char_count(candidate) <= TWEET_MAX:
        return candidate

    candidate = f"{title}\n\n{hashtags}\n\n{url}"
    if char_count(candidate) <= TWEET_MAX:
        return candidate

    fixed_tail = f"\n\n{hashtags}\n\n{url}"
    title_budget = TWEET_MAX - char_count(fixed_tail) - 1  # 1 for ellipsis
    title_budget = max(20, title_budget)
    truncated = title[: title_budget - 1].rstrip() + "…"
    return truncated + fixed_tail


def deliver(*, kind_label: str, dedup_slug: str | None, tweet_text: str, delivery: str, client) -> int:
    """Either post the tweet through tweepy (live) or send it as a draft to TG.
    On live success or draft success, mark dedup_slug as announced (if given).
    """
    chars = char_count(tweet_text)
    if delivery == "draft":
        rc = send_draft_to_telegram(kind_label=kind_label, tweet_text=tweet_text, char_total=chars)
    else:
        print(f"Posting {kind_label} ({chars}/280):\n{tweet_text}\n")
        try:
            resp = client.create_tweet(text=tweet_text)
            tid = resp.data.get("id") if resp and getattr(resp, "data", None) else None
            print(f"Posted: tweet_id={tid}")
            rc = 0
        except Exception as e:
            print(f"FAIL post: {type(e).__name__}: {e}", file=sys.stderr)
            rc = 1
    if rc == 0 and dedup_slug:
        conn = db_init()
        mark_announced(conn, dedup_slug, "news")
    return rc


def post_news(client, delivery: str) -> int:
    conn = db_init()
    found = find_next_news(conn)
    if not found:
        print("No new EN news to post on X.")
        return 0
    slug, fm = found
    title = (fm.get("title") or "").strip()
    summary = (fm.get("summary") or "").strip()
    tags = fm.get("tags") or []
    url = f"{SITE}/news/{slug}"
    if not url_is_live(url):
        print(f"Article URL not live yet: {url} — skipping; will retry next cron.")
        return 0
    text = build_news_tweet(title, summary, tags, url)
    return deliver(kind_label="News", dedup_slug=slug, tweet_text=text, delivery=delivery, client=client)


def post_fomo(client, delivery: str) -> int:
    line = random.choice(FOMO_LINES)
    url = f"{SITE}/culo"
    hashtags = pick_hashtags(niche_count=2)
    text = f"{line}\n\n{hashtags}\n\n{url}"
    if char_count(text) > TWEET_MAX:
        text = f"{line}\n\n{url}"
    return deliver(kind_label="FOMO", dedup_slug=None, tweet_text=text, delivery=delivery, client=client)


def post_mcap(client, delivery: str) -> int:
    data = fetch_culo_data()
    if not data or data.get("price") is None:
        print("Could not fetch $CULOTON data from GeckoTerminal — skipping (no-op).", file=sys.stderr)
        return 0
    pulse = "📈" if (data.get("change_h24") or 0) >= 0 else "📉"
    tagline = random.choice(MCAP_TAGLINES)
    hashtags = pick_hashtags(niche_count=2)
    url = f"{SITE}/culo"

    # Companion $CTAX line — kept on a single row to fit X's 280-char
    # budget. Shows live numbers when a pool exists, otherwise just the
    # tax mechanic so the community knows about the token.
    ctax = fetch_ctax_data()
    if ctax and ctax.get("price") is not None:
        ctax_pulse = "📈" if (ctax.get("change_h24") or 0) >= 0 else "📉"
        ctax_line = (
            f"$CTAX ({CTAX_TAX['buy']}b/{CTAX_TAX['sell']}s, {CTAX_TAX['holders_share']}%→holders): "
            f"{ctax_pulse} {fmt_money(ctax['price'])} ({fmt_change(ctax['change_h24'])} 24h)"
        )
    else:
        ctax_line = (
            f"$CTAX companion: {CTAX_TAX['buy']}% buy / {CTAX_TAX['sell']}% sell tax, "
            f"{CTAX_TAX['holders_share']}% → holders. Ownership renounced."
        )

    body = (
        f"$CULOTON market pulse\n"
        f"{pulse} {fmt_money(data['price'])} ({fmt_change(data['change_h24'])} 24h)\n"
        f"FDV {fmt_money(data['valuation'])} · Vol {fmt_money(data['vol_h24'])}\n\n"
        f"{ctax_line}\n\n"
        f"{tagline}\n\n"
        f"{hashtags}\n\n"
        f"{url}"
    )
    if char_count(body) > TWEET_MAX:
        body = (
            f"$CULOTON market pulse\n"
            f"{pulse} {fmt_money(data['price'])} ({fmt_change(data['change_h24'])} 24h)\n"
            f"FDV {fmt_money(data['valuation'])} · Vol {fmt_money(data['vol_h24'])}\n\n"
            f"{ctax_line}\n\n"
            f"{hashtags}\n\n"
            f"{url}"
        )
    if char_count(body) > TWEET_MAX:
        # Last-resort fallback: drop hashtags entirely, keep both tokens.
        body = (
            f"$CULOTON market pulse\n"
            f"{pulse} {fmt_money(data['price'])} ({fmt_change(data['change_h24'])} 24h)\n"
            f"FDV {fmt_money(data['valuation'])} · Vol {fmt_money(data['vol_h24'])}\n\n"
            f"{ctax_line}\n\n"
            f"{url}"
        )
    return deliver(kind_label="Market pulse", dedup_slug=None, tweet_text=body, delivery=delivery, client=client)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=("news", "fomo", "mcap"))
    args = p.parse_args()

    delivery = get_delivery_mode()
    if delivery == "noop":
        print("Neither X live keys nor TG draft chat configured — skipping (no-op).")
        return 0
    print(f"Delivery mode: {delivery}")

    client = get_client() if delivery == "live" else None

    if args.mode == "news":
        return post_news(client, delivery)
    if args.mode == "mcap":
        return post_mcap(client, delivery)
    return post_fomo(client, delivery)


if __name__ == "__main__":
    sys.exit(main())
