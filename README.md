# CuloTon

English-language news platform covering the TON blockchain ecosystem.
Native token: **$CULOTON** (TON contract `EQAYaqIikryTucQEz3IGRC62M7Eo4rzvduFAV5iWZ1b0A2Uc`).

Live: https://culoton.fun

## Structure

- `scripts/` — Python pipeline: pull RSS feeds, dedup, rewrite via Claude Haiku, write markdown.
- `web/` — Astro static site (dark theme, content collection from `web/src/content/news/`).
- `.github/workflows/update-and-deploy.yml` — every 2h: fetch news, rebuild, FTP-deploy to seohost.

## Local dev

```sh
# backend
pip install -r requirements.txt
cp .env.example .env  # fill ANTHROPIC_API_KEY
python scripts/fetch_news.py

# frontend
cd web
npm install
npm run dev
```

## Secrets (GitHub Actions)

- `ANTHROPIC_API_KEY` — used by the rewriter
- `FTP_USER`, `FTP_HOST`, `FTP_PASSWORD` — deploy credentials
