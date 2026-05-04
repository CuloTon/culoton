"""CuloTon news fetcher.

Pipeline:
1. Pull RSS feeds from sources.py
2. Skip entries already in seen.db (dedup by canonical URL)
3. Filter by keywords if source defines them
4. Rewrite each new entry through Claude Haiku 4.5 as a 200-400 word
   English article (JSON output: title, summary, body_markdown, tags)
5. Write markdown file with frontmatter to web/src/content/news/

Run locally:  python scripts/fetch_news.py
Run in CI:    same, with ANTHROPIC_API_KEY in env
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser
from anthropic import Anthropic
from dotenv import load_dotenv
from slugify import slugify

from sources import SOURCES

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(__file__).resolve().parent / "seen.db"
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
MODEL = "claude-haiku-4-5-20251001"
MAX_PER_SOURCE = 5  # cap per run so a fresh feed doesn't burn the budget
RETRY_LIMIT = 2

REWRITE_SYSTEM = """You are a crypto news editor for CuloTon, an English-language news site about the TON blockchain ecosystem. Rewrite source articles in original wording (no copying), in a clear journalistic tone, 200-400 words. Do not invent facts beyond what is in the source. Always close on a neutral, factual note.

Output strict JSON only — no prose, no code fences."""

REWRITE_USER_TEMPLATE = """Rewrite the following TON-related article for CuloTon.

ORIGINAL TITLE: {title}
ORIGINAL SOURCE: {source_name}
ORIGINAL URL: {url}

ORIGINAL CONTENT:
{content}

Output JSON with exactly these keys:
{{
  "title": "Punchy English headline, max 80 chars, no clickbait",
  "summary": "1-2 sentence dek for the news card, max 180 chars",
  "body_markdown": "200-400 words, paragraphs separated by blank lines, no headings",
  "tags": ["3-6 lowercase tags, e.g. ton, defi, toncoin, telegram"]
}}"""


def db_init() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS seen (
            url TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def already_seen(conn: sqlite3.Connection, url: str) -> bool:
    cur = conn.execute("SELECT 1 FROM seen WHERE url = ?", (url,))
    return cur.fetchone() is not None


def mark_seen(conn: sqlite3.Connection, url: str, source: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO seen (url, source, fetched_at) VALUES (?, ?, ?)",
        (url, source, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def matches_keywords(text: str, keywords: list[str] | None) -> bool:
    """Match if any keyword pattern (regex, case-insensitive) is found in text.

    Patterns should use word boundaries (\\b) to avoid false positives —
    e.g. \\btoncoin\\b will not match inside 'Cantonese' or 'Boston'.
    """
    if not keywords:
        return True
    return any(re.search(kw, text, re.IGNORECASE) for kw in keywords)


def clean_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def extract_content(entry) -> str:
    if hasattr(entry, "content") and entry.content:
        raw = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        raw = entry.summary
    elif hasattr(entry, "description"):
        raw = entry.description
    else:
        raw = ""
    return clean_html(raw)[:4000]


def parse_published(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def rewrite_article(client: Anthropic, *, title: str, source_name: str, url: str, content: str) -> dict:
    user = REWRITE_USER_TEMPLATE.format(
        title=title,
        source_name=source_name,
        url=url,
        content=content,
    )
    last_err = None
    for attempt in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=1500,
                system=REWRITE_SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(block.text for block in msg.content if block.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Rewrite failed after {RETRY_LIMIT + 1} attempts: {last_err}")


def write_markdown(*, published: datetime, source_name: str, source_url: str, original_url: str, rewritten: dict) -> Path:
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = published.strftime("%Y-%m-%d")
    slug = slugify(rewritten["title"])[:80] or slugify(original_url)[:80]
    path = NEWS_DIR / f"{date_str}-{slug}.md"

    if path.exists():
        path = NEWS_DIR / f"{date_str}-{slug}-{int(time.time())}.md"

    title_escaped = rewritten["title"].replace('"', '\\"')
    summary_escaped = rewritten["summary"].replace('"', '\\"')
    tags_yaml = "[" + ", ".join(json.dumps(t) for t in rewritten.get("tags", [])) + "]"

    frontmatter = (
        "---\n"
        f'title: "{title_escaped}"\n'
        f'summary: "{summary_escaped}"\n'
        f"date: {published.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f'source_name: "{source_name}"\n'
        f'source_url: "{source_url}"\n'
        f'original_url: "{original_url}"\n'
        f"tags: {tags_yaml}\n"
        "---\n\n"
    )
    path.write_text(frontmatter + rewritten["body_markdown"].strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY missing in .env", file=sys.stderr)
        return 1

    client = Anthropic(api_key=api_key)
    conn = db_init()

    total_new = 0
    total_skipped = 0
    total_errors = 0

    for source in SOURCES:
        print(f"\n[{source['name']}] fetching {source['feed']}")
        feed = feedparser.parse(source["feed"])
        if feed.bozo and not feed.entries:
            print(f"  feed error: {feed.bozo_exception}")
            continue

        per_source = 0
        for entry in feed.entries:
            if per_source >= MAX_PER_SOURCE:
                break

            url = entry.get("link", "").strip()
            if not url:
                continue

            if already_seen(conn, url):
                total_skipped += 1
                continue

            title = clean_html(entry.get("title", ""))
            content = extract_content(entry)

            if not matches_keywords(f"{title} {content}", source.get("keywords")):
                mark_seen(conn, url, source["name"])
                total_skipped += 1
                continue

            print(f"  rewriting: {title[:70]}")
            try:
                rewritten = rewrite_article(
                    client,
                    title=title,
                    source_name=source["name"],
                    url=url,
                    content=content,
                )
                published = parse_published(entry)
                path = write_markdown(
                    published=published,
                    source_name=source["name"],
                    source_url=source["url"],
                    original_url=url,
                    rewritten=rewritten,
                )
                mark_seen(conn, url, source["name"])
                total_new += 1
                per_source += 1
                print(f"  -> {path.name}")
            except Exception as e:
                print(f"  ERROR: {e}")
                total_errors += 1

    print(f"\nDone. new={total_new} skipped={total_skipped} errors={total_errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
