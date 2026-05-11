"""CuloTon news fetcher — multilingual edition (EN/RU/PL/DE/ES/UK).

Pipeline:
1. Pull RSS feeds from sources.py
2. Skip entries already in seen.db (dedup by canonical URL)
3. Filter by keywords if source defines them
4. Rewrite each new entry through Claude Haiku 4.5 in CuloScribe voice —
   one API call returns the article in EN, RU, PL and DE.
5. Write four markdown files (one per locale) with shared slug and metadata
   to web/src/content/news/{locale}/

Run locally:  python scripts/fetch_news.py
Run in CI:    same, with ANTHROPIC_API_KEY in env
"""

from __future__ import annotations

import json
import os
import re
import socket
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

# Cap socket reads so a slow/dead feed cannot wedge the whole job.
# Anthropic SDK uses httpx, which has its own timeouts and ignores this.
socket.setdefaulttimeout(20)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(__file__).resolve().parent / "seen.db"
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
MODEL = "claude-haiku-4-5-20251001"
MAX_PER_SOURCE = 5
RETRY_LIMIT = 2
USER_AGENT = "CuloTon-NewsBot/1.0 (+https://culoton.fun)"

LOCALES = ("en", "ru", "pl", "de", "es", "uk")

CULOSCRIBE_SYSTEM = """You are CuloScribe — the editorial AI for CuloTon, an independent news desk covering the TON blockchain ecosystem.

# Voice
You are a witty journalist with a serious edge. Think Financial Times reporter who sometimes lets a sharp observation slip in. Your default register is clear, factual, journalistic. You add a light wry note where it fits — especially for community, memecoin, or culture stories — but you stay strictly serious for:
- security incidents and exploits
- regulatory and legal news
- technical protocol details
- significant market moves and price reporting
- statements from named individuals or institutions

Never goofy. Never cringe. The humor is in dry phrasing, never in jokes about the topic itself.

# Copyright and originality (CRITICAL)
You are NOT translating or copying. You are RE-REPORTING. You read the source, understand the substance, and re-write it in your own words, with your own structure, as a journalist would for their own publication.

- Never reuse phrases or sentence structures from the source
- Paraphrase the facts; do not paraphrase the prose
- Build your own narrative arc (lede → context → details → what-it-means)
- Add journalistic framing the source may lack: why-it-matters context, neutral interpretation
- Never invent facts beyond what is in the source. If the source is thin, the article is short. Better honest than padded.
- Always close on a neutral, factual note. No editorial calls to action.

# Multilingual output
You produce the article in six languages: English (en), Russian (ru), Polish (pl), German (de), Spanish (es), Ukrainian (uk). Each version is a NATIVE rewrite, not a translation — natural idioms, natural rhythm for that language. The facts must match across all six versions, but the phrasing must be independent.

# Length
Each language version: 200-400 words in body_markdown. Paragraphs separated by blank lines. No headings inside body.

# Output format
Strict JSON only. No prose outside JSON. No code fences."""

CULOSCRIBE_USER_TEMPLATE = """Re-report the following TON-related article for CuloTon, in your own words, in four languages.

ORIGINAL TITLE: {title}
ORIGINAL SOURCE: {source_name}
ORIGINAL URL: {url}

ORIGINAL CONTENT:
{content}

Output JSON with exactly these keys:
{{
  "tags": ["3-6 lowercase tags, e.g. ton, defi, toncoin, telegram"],
  "en": {{
    "title": "Punchy English headline, max 80 chars, no clickbait",
    "summary": "1-2 sentence dek for the news card, max 180 chars",
    "body_markdown": "200-400 words, paragraphs separated by blank lines, no headings"
  }},
  "ru": {{
    "title": "Заголовок на русском, max 80 chars",
    "summary": "Краткое описание, max 180 chars",
    "body_markdown": "Статья на русском, 200-400 слов"
  }},
  "pl": {{
    "title": "Polski tytul, max 80 chars",
    "summary": "Krotki opis, max 180 znakow",
    "body_markdown": "Artykul po polsku, 200-400 slow"
  }},
  "de": {{
    "title": "Deutsche Schlagzeile, max 80 chars",
    "summary": "Kurze Beschreibung, max 180 Zeichen",
    "body_markdown": "Deutscher Artikel, 200-400 Worter"
  }},
  "es": {{
    "title": "Titular en espanol, max 80 chars",
    "summary": "Resumen breve, max 180 caracteres",
    "body_markdown": "Articulo en espanol, 200-400 palabras"
  }},
  "uk": {{
    "title": "Заголовок українською, max 80 chars",
    "summary": "Короткий опис, max 180 символів",
    "body_markdown": "Стаття українською, 200-400 слів"
  }}
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
    user = CULOSCRIBE_USER_TEMPLATE.format(
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
                max_tokens=4500,
                system=CULOSCRIBE_SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(block.text for block in msg.content if block.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            for loc in LOCALES:
                if loc not in data or not isinstance(data[loc], dict):
                    raise ValueError(f"missing locale block: {loc}")
                for key in ("title", "summary", "body_markdown"):
                    if key not in data[loc] or not data[loc][key]:
                        raise ValueError(f"missing {loc}.{key}")
            if "tags" not in data:
                data["tags"] = []
            return data
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Rewrite failed after {RETRY_LIMIT + 1} attempts: {last_err}")


def write_markdown_set(*, published: datetime, source_name: str, source_url: str, original_url: str, rewritten: dict) -> list[Path]:
    """Write one markdown file per locale, sharing the same slug.

    The slug is derived from the English title so URLs line up across locales:
      /news/<slug>          → English
      /<locale>/news/<slug> → other languages
    """
    date_str = published.strftime("%Y-%m-%d")
    en_title = rewritten["en"]["title"]
    base_slug = slugify(en_title)[:80] or slugify(original_url)[:80]
    suffix = ""
    written: list[Path] = []

    # Resolve a shared suffix once (collision check on EN file).
    en_dir = NEWS_DIR / "en"
    en_dir.mkdir(parents=True, exist_ok=True)
    candidate = en_dir / f"{date_str}-{base_slug}.md"
    if candidate.exists():
        suffix = f"-{int(time.time())}"

    tags_yaml = "[" + ", ".join(json.dumps(t) for t in rewritten.get("tags", [])) + "]"
    iso_date = published.strftime("%Y-%m-%dT%H:%M:%SZ")

    for loc in LOCALES:
        loc_dir = NEWS_DIR / loc
        loc_dir.mkdir(parents=True, exist_ok=True)
        path = loc_dir / f"{date_str}-{base_slug}{suffix}.md"

        block = rewritten[loc]
        title_escaped = block["title"].replace('"', '\\"')
        summary_escaped = block["summary"].replace('"', '\\"')

        frontmatter = (
            "---\n"
            f"locale: {loc}\n"
            f'title: "{title_escaped}"\n'
            f'summary: "{summary_escaped}"\n'
            f"date: {iso_date}\n"
            f'source_name: "{source_name}"\n'
            f'source_url: "{source_url}"\n'
            f'original_url: "{original_url}"\n'
            f"tags: {tags_yaml}\n"
            "---\n\n"
        )
        path.write_text(frontmatter + block["body_markdown"].strip() + "\n", encoding="utf-8")
        written.append(path)

    return written


def main() -> int:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        # Strip BOM and whitespace — PowerShell pipe → `gh secret set` on Windows
        # has been known to embed CRLF or UTF-8 BOM, which crashes httpx
        # header encoding.
        api_key = api_key.lstrip("﻿").strip()
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
        try:
            feed = feedparser.parse(source["feed"], agent=USER_AGENT)
        except Exception as e:
            print(f"  feed fetch failed: {type(e).__name__}: {e}")
            continue
        if feed.bozo and not feed.entries:
            print(f"  feed error: {feed.bozo_exception}")
            continue
        print(f"  entries: {len(feed.entries)}")

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
                paths = write_markdown_set(
                    published=published,
                    source_name=source["name"],
                    source_url=source["url"],
                    original_url=url,
                    rewritten=rewritten,
                )
                mark_seen(conn, url, source["name"])
                total_new += 1
                per_source += 1
                print(f"  -> {paths[0].name} (×{len(paths)} locales)")
            except Exception as e:
                print(f"  ERROR: {e}")
                total_errors += 1

    print(f"\nDone. new={total_new} skipped={total_skipped} errors={total_errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
