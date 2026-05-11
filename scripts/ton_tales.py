"""CuloTon "TON Tales" generator.

Once a week, read the most recent CuloTon coverage (news + community pulse)
and ask CuloScribe to weave it into ONE narrative piece — a chronicle / vignette
/ essay with a story arc, told in a register the material supports (fun,
interesting, or quietly inspiring). The facts stay real; only the framing and
pacing are dramatized.

If the material can't honestly support a worthwhile story, CuloScribe returns
`{"skip": true, "reason": "..."}` and nothing is written. Quality over cadence —
a skipped week is fine.

Output: one markdown file per locale under web/src/content/tale/{locale}/,
sharing a slug derived from the English title.

Usage:
    python scripts/ton_tales.py            # generate this week's tale (if any)
    python scripts/ton_tales.py --force    # regenerate even if today's file exists

The script is idempotent: if a tale already exists for today's date it exits 0
without calling the API (unless --force).
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
from slugify import slugify

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
PULSE_DIR = ROOT / "web" / "src" / "content" / "pulse"
TALE_DIR = ROOT / "web" / "src" / "content" / "tale"
MODEL = "claude-haiku-4-5-20251001"
RETRY_LIMIT = 2
LOCALES = ("en", "ru", "pl", "de", "es", "uk")

# How much raw material to feed the model.
NEWS_INPUT_COUNT = 16
PULSE_INPUT_COUNT = 3
NEWS_BODY_CLIP = 1300
PULSE_BODY_CLIP = 900

CULOSCRIBE_SYSTEM = """You are CuloScribe — the editorial AI for CuloTon, an independent news desk covering the TON blockchain ecosystem.

Today you are NOT writing a news article and NOT writing a roundup. You are writing a **TON Tale** — a single narrative piece that turns the recent TON-ecosystem developments you are given into ONE story with a real arc.

# What a TON Tale is
- A chronicle, a vignette, or a short essay with narrative shape — beginning, middle, a turn, a landing.
- It can be fun, interesting, or quietly inspiring. Pick the register the material actually supports. If the week was a string of small wins, write something hopeful. If it was a comedy of memecoins and mini-apps, let the wit show. If it was a hard week (an exploit, a delay), the tale is more sober — never glib about a security incident.
- It reads like a piece a human columnist would be proud of: voice, rhythm, a point of view. Not a digest. Not a list of links.

# The hard rule: facts are real
- Every event, number, name, project, quote and claim in the tale must come from the material provided. You may dramatize framing, pacing, perspective, ordering and connective tissue — you may NOT invent events, statistics, people, quotes or outcomes that are not in the source.
- If something in the source is reported/speculative, treat it as such inside the narrative — do not harden rumour into fact for the sake of a better story.
- No editorial calls to action, no price predictions, no investment advice. Close on a forward-looking but neutral note.

# When to skip
If the material is thin, disjointed, or simply can't honestly carry a worthwhile story, do not force one. Return `{"skip": true, "reason": "<one sentence>"}` and write nothing. A skipped week is completely fine.

# The token
Do NOT shill or pitch $CULOTON inside the tale. The site as a whole carries the brand; the tale stays clean editorial.

# Multilingual output
Produce the tale in six languages: English (en), Russian (ru), Polish (pl), German (de), Spanish (es), Ukrainian (uk). Each version is a NATIVE piece — natural idiom and rhythm for that language, not a literal translation. The facts and the arc match across all six; the prose is independent.

# Length
Each language version: 600-1000 words in body_markdown. Paragraphs separated by blank lines. You may use **bold lead phrases** to mark beats, but NO markdown headings (no "#") inside the body.

# Output format
Strict JSON only. No prose outside JSON. No code fences."""

CULOSCRIBE_USER_TEMPLATE = """Below is CuloTon's recent coverage of the TON ecosystem — {n_news} news items and {n_pulse} community-pulse notes, newest first. Read across all of it, find the thread, and write ONE TON Tale, in your editorial voice, across six languages. Or skip if it can't honestly carry a story.

=== RECENT NEWS (newest first) ===
{news_block}

=== RECENT COMMUNITY PULSE (newest first) ===
{pulse_block}

Output strict JSON. If you write a tale:
{{
  "skip": false,
  "tags": ["3-6 lowercase tags, e.g. ton, telegram, defi, story"],
  "en": {{
    "title": "Evocative title for the tale, max 80 chars, no clickbait",
    "summary": "1-2 sentence dek that sets the scene, max 200 chars",
    "body_markdown": "600-1000 words, paragraphs separated by blank lines, optional bold lead phrases, NO headings, no $CULOTON pitch"
  }},
  "ru": {{ "title": "...", "summary": "...", "body_markdown": "..." }},
  "pl": {{ "title": "...", "summary": "...", "body_markdown": "..." }},
  "de": {{ "title": "...", "summary": "...", "body_markdown": "..." }},
  "es": {{ "title": "...", "summary": "...", "body_markdown": "..." }},
  "uk": {{ "title": "...", "summary": "...", "body_markdown": "..." }}
}}

If you skip:
{{ "skip": true, "reason": "<one sentence why the material can't carry a worthwhile tale>" }}"""


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    if not md_text.startswith("---"):
        return {}, md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}, md_text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        fm = {}
    body = parts[2].lstrip("\n")
    return fm, body


def collect_recent(dir_en: Path, limit: int) -> list[tuple[str, dict, str]]:
    """Return [(filename, frontmatter, body)] for the N most recent .md files in
    a directory's EN subfolder, newest first by frontmatter date.
    """
    if not dir_en.exists():
        return []
    items: list[tuple[str, dict, str]] = []
    for path in dir_en.glob("*.md"):
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


def build_block(items: list[tuple[str, dict, str]], *, clip: int, kind: str) -> str:
    if not items:
        return "(none)"
    blocks = []
    for idx, (fname, fm, body) in enumerate(items, 1):
        body_clip = body.strip()
        if len(body_clip) > clip:
            body_clip = body_clip[:clip].rsplit(" ", 1)[0] + "..."
        meta = f"TITLE: {fm.get('title', '')}\nDATE: {fm.get('date', '')}"
        if kind == "news":
            meta += f"\nSOURCE: {fm.get('source_name', '')}"
        blocks.append(f"--- {kind.upper()} {idx} ---\n{meta}\nBODY:\n{body_clip}\n")
    return "\n".join(blocks)


def call_haiku(client: Anthropic, *, news_block: str, pulse_block: str, n_news: int, n_pulse: int) -> dict:
    user = CULOSCRIBE_USER_TEMPLATE.format(
        news_block=news_block,
        pulse_block=pulse_block,
        n_news=n_news,
        n_pulse=n_pulse,
    )
    last_err = None
    for attempt in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=9000,
                system=CULOSCRIBE_SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            if data.get("skip"):
                return {"skip": True, "reason": str(data.get("reason", "no reason given"))}
            for loc in LOCALES:
                if loc not in data or not isinstance(data[loc], dict):
                    raise ValueError(f"missing locale block: {loc}")
                for key in ("title", "summary", "body_markdown"):
                    if not data[loc].get(key):
                        raise ValueError(f"missing {loc}.{key}")
            data.setdefault("tags", [])
            data["skip"] = False
            return data
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Tale synthesis failed after {RETRY_LIMIT + 1} attempts: {last_err}")


def write_tale(*, generated_at: datetime, articles_covered: list[str], data: dict) -> list[Path]:
    date_str = generated_at.strftime("%Y-%m-%d")
    iso_date = generated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    en_title = data["en"]["title"]
    base_slug = (slugify(en_title)[:70] or "ton-tale").strip("-")
    slug = f"{date_str}-{base_slug}"

    # Collision guard on the EN file.
    en_dir = TALE_DIR / "en"
    en_dir.mkdir(parents=True, exist_ok=True)
    if (en_dir / f"{slug}.md").exists():
        slug = f"{slug}-{int(time.time())}"

    tags_yaml = "[" + ", ".join(json.dumps(t) for t in data.get("tags", [])) + "]"
    covered_yaml = "[" + ", ".join(json.dumps(s) for s in articles_covered) + "]"
    written: list[Path] = []
    for loc in LOCALES:
        loc_dir = TALE_DIR / loc
        loc_dir.mkdir(parents=True, exist_ok=True)
        path = loc_dir / f"{slug}.md"
        block = data[loc]
        title_escaped = block["title"].replace('"', '\\"')
        summary_escaped = block["summary"].replace('"', '\\"')
        frontmatter = (
            "---\n"
            f"locale: {loc}\n"
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
    parser.add_argument("--force", action="store_true", help="Regenerate even if today's tale exists")
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

    # Idempotency: skip if any EN tale already dated today.
    en_dir = TALE_DIR / "en"
    if not args.force and en_dir.exists() and any(en_dir.glob(f"{date_str}-*.md")):
        print(f"A TON Tale already exists for {date_str} — skipping (use --force to regenerate).")
        return 0

    news_items = collect_recent(NEWS_DIR / "en", NEWS_INPUT_COUNT)
    pulse_items = collect_recent(PULSE_DIR / "en", PULSE_INPUT_COUNT)
    if len(news_items) < 4:
        print(f"Not enough recent news to attempt a tale ({len(news_items)} found, need >=4). Skipping.")
        return 0

    news_block = build_block(news_items, clip=NEWS_BODY_CLIP, kind="news")
    pulse_block = build_block(pulse_items, clip=PULSE_BODY_CLIP, kind="pulse")
    articles_covered = [fname for fname, _, _ in news_items]

    client = Anthropic(api_key=api_key)
    print(f"Synthesising a TON Tale from {len(news_items)} news + {len(pulse_items)} pulse items...")
    data = call_haiku(
        client,
        news_block=news_block,
        pulse_block=pulse_block,
        n_news=len(news_items),
        n_pulse=len(pulse_items),
    )

    if data.get("skip"):
        print(f"CuloScribe declined to write a tale: {data.get('reason')}")
        return 0

    paths = write_tale(generated_at=now_utc, articles_covered=articles_covered, data=data)
    print(f"Wrote TON Tale: {paths[0].name} (x{len(paths)} locales)")
    print(f"  Title: {data['en']['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
