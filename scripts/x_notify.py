"""CuloTon X (Twitter) notifier.

Two modes:

  --mode news
      Picks the newest EN article that has not yet been tweeted,
      builds a 280-char tweet (title + summary if it fits + a few
      hashtags + link to culoton.fun) and posts it. Marks the
      article as announced in scripts/x_announced.db.

  --mode fomo
      Posts a randomised one-liner about CuloTon's role in the TON
      ecosystem with #TON #CULO hashtags and a link to /culo.

Both modes are graceful no-ops when any of the four X OAuth 1.0a
secrets is missing — so the workflow can be merged before keys
are configured.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    import tweepy
except ImportError:
    tweepy = None  # graceful no-op when dep missing

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
    "TON is quietly eating 2026. CuloTon publishes the receipts. $CULO is along for the ride.",
    "Three previous chains, one narrative. $CULO came home — and home is on TON.",
    "We don't shill TON. We publish three roundups a day about it. Coincidence? No. $CULO",
    "Telegram is the chat. TON is the chain. $CULO is the meme that ties them.",
    "Sub-second blocks on TON. Sub-280-character takes from CuloTon. $CULO is the punchline.",
    "Most projects shill. CuloTon publishes. Then we mention $CULO — lightly.",
    "If TON wins, $CULO wins. Track record: 10,000X on Polygon, then SUI, now TON.",
    "Small cap. Big chain. Attentive crew. $CULO on TON — and we're just clearing our throat.",
    "Don't bet on TON. Be on it. $CULO is one of many ways.",
    "Build the media voice first, the bag follows. CuloTon → $CULO → TON. In that order.",
    "While altcoins fight for relevance, TON ships and CuloTon writes it down. $CULO funds the desk.",
    "The fastest chain in crypto runs the most-used messenger on Earth. $CULO is the meme leg.",
]


def get_client():
    ck = (os.getenv("X_CONSUMER_KEY") or "").strip()
    cs = (os.getenv("X_CONSUMER_SECRET") or "").strip()
    at = (os.getenv("X_ACCESS_TOKEN") or "").strip()
    ats = (os.getenv("X_ACCESS_TOKEN_SECRET") or "").strip()
    if not all([ck, cs, at, ats]):
        return None
    if tweepy is None:
        print("tweepy not installed — install via requirements.txt", file=sys.stderr)
        return None
    return tweepy.Client(
        consumer_key=ck,
        consumer_secret=cs,
        access_token=at,
        access_token_secret=ats,
    )


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


def post_news(client) -> int:
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
    text = build_news_tweet(title, summary, tags, url)
    print(f"Posting news tweet ({char_count(text)} chars):\n{text}\n")
    try:
        resp = client.create_tweet(text=text)
        tid = resp.data.get("id") if resp and getattr(resp, "data", None) else None
        print(f"Posted: tweet_id={tid}")
        mark_announced(conn, slug, "news")
        return 0
    except Exception as e:
        print(f"FAIL post_news: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


def post_fomo(client) -> int:
    line = random.choice(FOMO_LINES)
    url = f"{SITE}/culo"
    hashtags = pick_hashtags(niche_count=2)  # 2 core + 2 niche = 4 total
    text = f"{line}\n\n{hashtags}\n\n{url}"
    if char_count(text) > TWEET_MAX:
        # Fallback: drop hashtags if line itself is unusually long
        text = f"{line}\n\n{url}"
    print(f"Posting fomo tweet ({char_count(text)} chars):\n{text}\n")
    try:
        resp = client.create_tweet(text=text)
        tid = resp.data.get("id") if resp and getattr(resp, "data", None) else None
        print(f"Posted: tweet_id={tid}")
        return 0
    except Exception as e:
        print(f"FAIL post_fomo: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=("news", "fomo"))
    args = p.parse_args()

    client = get_client()
    if client is None:
        print("X credentials missing or tweepy unavailable — skipping (no-op).")
        return 0

    if args.mode == "news":
        return post_news(client)
    return post_fomo(client)


if __name__ == "__main__":
    sys.exit(main())
