"""CuloTon blog roundup generator.

Three times a day (morning / noon / evening) read the most recent EN news
and synthesise them into one editorial blog post in 4 languages.

Usage:
    python scripts/blog_roundup.py --kind morning
    python scripts/blog_roundup.py --kind noon
    python scripts/blog_roundup.py --kind evening

The script is idempotent: if a roundup file already exists for today's date
and the requested kind, it exits 0 without calling the API. This makes it
safe to re-run from the same scheduled slot.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
BLOG_DIR = ROOT / "web" / "src" / "content" / "blog"
MODEL = "claude-haiku-4-5-20251001"
RETRY_LIMIT = 2
LOCALES = ("en", "ru", "pl", "de")

# How many recent EN news entries to feed into each roundup.
ROUNDUP_INPUT_COUNT = 10

KIND_HEADLINE = {
    "morning": "morning",
    "noon": "midday",
    "evening": "evening",
}

CULOSCRIBE_SYSTEM = """You are CuloScribe — the editorial AI for CuloTon, an independent news desk covering the TON blockchain ecosystem.

Today you are not writing a news article. You are writing a **roundup blog post** — a single editorial brief that stitches together the most recent TON-ecosystem news into one read for someone who has been away for a few hours.

# Voice
Witty journalist with a serious edge — Financial Times-style. Default register: clear, factual, journalistic. A dry observation is welcome where it fits the topic. Never goofy. Never cringe. The humour lives in dry phrasing, never in jokes about the subject.

For market moves, security incidents, regulatory news and technical detail — strictly serious. For community and culture — a light touch is allowed.

# Format of the roundup
- A single editorial piece, 350-550 words in body_markdown.
- Open with a 1-2 sentence lede that captures the dominant theme of the period (what was THE story in the last few hours).
- Then 3-5 short sections separated by blank lines. Each section is one paragraph. Use **bold lead phrases** (NOT markdown headings) to mark each subtopic — e.g. "**On the validator front,** ..." or "**In DeFi,** ...". No "##" headings inside the body.
- Close with one neutral sentence framing what to watch next. No calls to action, no investment advice.

Do NOT mention $CULOTON inside the roundup body. The roundup is about TON, not the token. The site as a whole signals the brand; the editorial stays clean.

# Sourcing
You will be given the full text of recent CuloTon news articles. Synthesise across them — show connections, group related events, distinguish what is confirmed from what is reported/speculative. You may quote a specific source name in passing (e.g. "according to BeInCrypto") but do not bullet-list every source. The roundup is a synthesis, not a digest.

If two articles disagree, briefly acknowledge the disagreement. If the period was quiet, the roundup is shorter and says so.

# Multilingual output
Produce the roundup in four languages: English (en), Russian (ru), Polish (pl), German (de). Each version is a NATIVE rewrite, not a translation — natural idioms, natural rhythm. Facts must match across all four versions; phrasing must be independent.

# Output format
Strict JSON only. No prose outside JSON. No code fences."""

CULOSCRIBE_USER_TEMPLATE = """Write the {kind} roundup for the TON ecosystem, dated {date_label}, in your editorial voice across four languages.

The {n} most recent CuloTon articles are below, in reverse-chronological order. Synthesise them into one brief — group related events, show the dominant theme, mention names and numbers where useful, but do not list articles individually.

ARTICLES (newest first):

{articles_block}

Output JSON with exactly these keys:
{{
  "tags": ["3-6 lowercase tags, e.g. roundup, ton, telegram, defi"],
  "en": {{
    "title": "Editorial title for the {kind} roundup, max 80 chars, no clickbait",
    "summary": "1-2 sentence dek that captures the dominant theme, max 200 chars",
    "body_markdown": "350-550 words, paragraphs separated by blank lines, bold lead phrases NOT headings, no $CULOTON references"
  }},
  "ru": {{
    "title": "Редакционный заголовок для {kind_label_ru} обзора, max 80 chars",
    "summary": "Краткое описание главной темы, max 200 chars",
    "body_markdown": "350-550 слов на русском, абзацы через пустую строку, жирные ведущие фразы вместо заголовков"
  }},
  "pl": {{
    "title": "Redakcyjny tytul {kind_label_pl} podsumowania, max 80 chars",
    "summary": "Krotki opis glownego watku, max 200 znakow",
    "body_markdown": "350-550 slow po polsku, akapity przedzielone pusta linia, pogrubione frazy wiodace zamiast naglowkow"
  }},
  "de": {{
    "title": "Redaktioneller Titel des {kind_label_de} Roundups, max 80 chars",
    "summary": "Kurze Beschreibung des Hauptthemas, max 200 Zeichen",
    "body_markdown": "350-550 Worter auf Deutsch, Absatze durch Leerzeile getrennt, fette Leitphrasen statt Uberschriften"
  }}
}}"""

KIND_LABELS = {
    "ru": {"morning": "утреннего", "noon": "дневного", "evening": "вечернего"},
    "pl": {"morning": "porannego", "noon": "poludniowego", "evening": "wieczornego"},
    "de": {"morning": "Morgen-", "noon": "Mittags-", "evening": "Abend-"},
}


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    if not md_text.startswith("---"):
        return {}, md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}, md_text
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return fm, body


def collect_recent_en_news(limit: int) -> list[tuple[str, dict, str]]:
    """Return [(file_id, frontmatter, body)] for the N most recent EN news files,
    sorted newest first by frontmatter date.
    """
    en_dir = NEWS_DIR / "en"
    if not en_dir.exists():
        return []
    items: list[tuple[str, dict, str]] = []
    for path in en_dir.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            if not fm.get("date"):
                continue
            items.append((path.name, fm, body))
        except Exception as e:
            print(f"  skip {path.name}: {e}", file=sys.stderr)
    items.sort(key=lambda x: str(x[1].get("date", "")), reverse=True)
    return items[:limit]


def build_articles_block(items: list[tuple[str, dict, str]]) -> str:
    blocks = []
    for idx, (fname, fm, body) in enumerate(items, 1):
        title = fm.get("title", "")
        source = fm.get("source_name", "")
        date = fm.get("date", "")
        # Trim each body to keep prompt cost reasonable.
        body_clip = body.strip()
        if len(body_clip) > 1400:
            body_clip = body_clip[:1400].rsplit(" ", 1)[0] + "..."
        blocks.append(
            f"--- ARTICLE {idx} ---\n"
            f"TITLE: {title}\n"
            f"DATE: {date}\n"
            f"SOURCE: {source}\n"
            f"BODY:\n{body_clip}\n"
        )
    return "\n".join(blocks)


def call_haiku(client: Anthropic, *, kind: str, date_label: str, articles_block: str, n: int) -> dict:
    user = CULOSCRIBE_USER_TEMPLATE.format(
        kind=kind,
        kind_label_ru=KIND_LABELS["ru"][kind],
        kind_label_pl=KIND_LABELS["pl"][kind],
        kind_label_de=KIND_LABELS["de"][kind],
        date_label=date_label,
        articles_block=articles_block,
        n=n,
    )
    last_err = None
    for attempt in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=6000,
                system=CULOSCRIBE_SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            for loc in LOCALES:
                if loc not in data or not isinstance(data[loc], dict):
                    raise ValueError(f"missing locale block: {loc}")
                for key in ("title", "summary", "body_markdown"):
                    if not data[loc].get(key):
                        raise ValueError(f"missing {loc}.{key}")
            data.setdefault("tags", [])
            return data
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Roundup synthesis failed after {RETRY_LIMIT + 1} attempts: {last_err}")


def write_roundup(*, kind: str, generated_at: datetime, articles_covered: list[str], data: dict) -> list[Path]:
    date_str = generated_at.strftime("%Y-%m-%d")
    iso_date = generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    slug_base = f"{date_str}-{kind}"
    tags_yaml = "[" + ", ".join(json.dumps(t) for t in data.get("tags", [])) + "]"
    covered_yaml = "[" + ", ".join(json.dumps(s) for s in articles_covered) + "]"
    written: list[Path] = []
    for loc in LOCALES:
        loc_dir = BLOG_DIR / loc
        loc_dir.mkdir(parents=True, exist_ok=True)
        path = loc_dir / f"{slug_base}.md"
        block = data[loc]
        title_escaped = block["title"].replace('"', '\\"')
        summary_escaped = block["summary"].replace('"', '\\"')
        frontmatter = (
            "---\n"
            f"locale: {loc}\n"
            f"kind: {kind}\n"
            f'title: "{title_escaped}"\n'
            f'summary: "{summary_escaped}"\n'
            f"date: {iso_date}\n"
            f"articles_covered: {covered_yaml}\n"
            f"tags: {tags_yaml}\n"
            "---\n\n"
        )
        path.write_text(frontmatter + block["body_markdown"].strip() + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True, choices=("morning", "noon", "evening"))
    parser.add_argument("--force", action="store_true", help="Regenerate even if today's file exists")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        api_key = api_key.lstrip("﻿").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY missing", file=sys.stderr)
        return 1

    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    target_path = BLOG_DIR / "en" / f"{date_str}-{args.kind}.md"

    if target_path.exists() and not args.force:
        print(f"Roundup already exists for {date_str}/{args.kind} — skipping (use --force to regenerate).")
        return 0

    items = collect_recent_en_news(ROUNDUP_INPUT_COUNT)
    if len(items) < 2:
        print(f"Not enough EN news to build a roundup ({len(items)} found, need >=2). Skipping.")
        return 0

    articles_block = build_articles_block(items)
    articles_covered = [f"en/{fname}" for fname, _, _ in items]
    date_label = now_utc.strftime("%B %d, %Y")

    print(f"Building {args.kind} roundup for {date_label} from {len(items)} EN articles...")
    client = Anthropic(api_key=api_key)
    data = call_haiku(client, kind=args.kind, date_label=date_label, articles_block=articles_block, n=len(items))

    paths = write_roundup(
        kind=args.kind,
        generated_at=now_utc,
        articles_covered=articles_covered,
        data=data,
    )
    print(f"Wrote {len(paths)} files:")
    for p in paths:
        print(f"  {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
