"""One-shot recovery: regenerate only the DE versions of existing articles.

Used after a Windows npm/install conflict wiped web/src/content/news/de/.
For each en/*.md, generate a de/*.md with the CuloScribe persona, single-locale
to keep cost minimal.
"""

from __future__ import annotations

import json
import os
import re
import socket
import sys
import time
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

socket.setdefaulttimeout(20)

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "web" / "src" / "content" / "news"
EN_DIR = NEWS_DIR / "en"
DE_DIR = NEWS_DIR / "de"
MODEL = "claude-haiku-4-5-20251001"
RETRY_LIMIT = 2

SYSTEM = """You are CuloScribe, the editorial AI for CuloTon — a witty journalist with a serious edge writing for German readers about the TON blockchain ecosystem.

Re-report the article in your own German words: own structure, own phrasing, your journalistic voice. Never translate sentence-for-sentence; never copy phrasing.

Tone: clear, factual, journalistic. Dry wit allowed for community/culture stories. Strictly serious for security incidents, regulatory news, technical detail, market moves, and statements from named individuals.

Length: 200-400 words. Paragraphs separated by blank lines. No headings inside body. No editorial calls to action.

Output strict JSON only. No prose outside JSON. No code fences."""

USER_TPL = """Re-report for CuloTon's German edition.

ORIGINAL TITLE: {title}
ORIGINAL SOURCE: {source_name}
ORIGINAL URL: {url}

ENGLISH BODY (do not translate phrase-for-phrase, re-report in German):
{content}

Output JSON:
{{
  "title": "Deutsche Schlagzeile, max 80 chars",
  "summary": "Kurze Beschreibung, max 180 chars",
  "body_markdown": "Deutscher Artikel, 200-400 Worter"
}}"""


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"no frontmatter in {path.name}")
    fm_text, body = m.group(1), m.group(2).strip()
    fm: dict = {}
    for line in fm_text.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            value = [s.strip().strip('"') for s in inner.split(",") if s.strip()] if inner else []
        fm[key] = value
    return {"fm": fm, "body": body}


def rewrite_de(client: Anthropic, *, title: str, source_name: str, url: str, content: str) -> dict:
    user = USER_TPL.format(title=title, source_name=source_name, url=url, content=content)
    last = None
    for attempt in range(RETRY_LIMIT + 1):
        try:
            msg = client.messages.create(
                model=MODEL,
                max_tokens=1500,
                system=SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            data = json.loads(text)
            for k in ("title", "summary", "body_markdown"):
                if k not in data or not data[k]:
                    raise ValueError(f"missing {k}")
            return data
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"DE rewrite failed: {last}")


def main() -> int:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        api_key = api_key.lstrip("﻿").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY missing", file=sys.stderr)
        return 1

    client = Anthropic(api_key=api_key)
    DE_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(EN_DIR.glob("*.md"))
    print(f"Found {len(files)} EN articles; regenerating DE for missing slugs only")

    ok, fail, skip = 0, 0, 0
    for i, path in enumerate(files, 1):
        slug = path.stem
        de_path = DE_DIR / f"{slug}.md"
        if de_path.exists():
            skip += 1
            continue

        print(f"\n[{i}/{len(files)}] {slug}")
        try:
            parsed = parse_md(path)
            fm = parsed["fm"]
            body = parsed["body"]
            data = rewrite_de(
                client,
                title=fm["title"],
                source_name=fm["source_name"],
                url=fm["original_url"],
                content=body,
            )

            tags_yaml = "[" + ", ".join(json.dumps(t) for t in fm.get("tags", [])) + "]"
            title_e = data["title"].replace('"', '\\"')
            summary_e = data["summary"].replace('"', '\\"')

            frontmatter = (
                "---\n"
                "locale: de\n"
                f'title: "{title_e}"\n'
                f'summary: "{summary_e}"\n'
                f"date: {fm['date']}\n"
                f'source_name: "{fm["source_name"]}"\n'
                f'source_url: "{fm["source_url"]}"\n'
                f'original_url: "{fm["original_url"]}"\n'
                f"tags: {tags_yaml}\n"
                "---\n\n"
            )
            de_path.write_text(frontmatter + data["body_markdown"].strip() + "\n", encoding="utf-8")
            print(f"  -> de/{de_path.name}")
            ok += 1
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}: {e}")
            fail += 1

    print(f"\nDone. ok={ok} skip={skip} fail={fail}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
