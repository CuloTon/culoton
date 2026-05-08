# culoton-stats — Cloudflare Worker

Tiny stats backend for culoton.fun. Tracks pageviews, online presence,
rolling averages. Storage: a single KV namespace.

## One-time setup (you only do this once)

You need a Cloudflare account (free tier is enough).

1. Install wrangler locally and log in:

   ```
   npm install
   npx wrangler login
   ```

2. Create the KV namespace and copy its `id` into `wrangler.toml`:

   ```
   npx wrangler kv namespace create stats
   ```

   Wrangler prints something like `id = "abcd1234..."`. Paste that
   into the `[[kv_namespaces]]` block in `wrangler.toml`.

3. First manual deploy (so the workers.dev subdomain is provisioned):

   ```
   npm run deploy
   ```

   The worker URL it prints (e.g. `https://culoton-stats.<acct>.workers.dev`)
   is the one the website talks to.

4. GitHub Action auto-deploy. Add two repo secrets:

   - `CF_API_TOKEN` — Cloudflare API token (template: "Edit Cloudflare Workers")
   - `CF_ACCOUNT_ID` — the account id wrangler shows on login

   Plus one repo secret used by the website build:

   - `PUBLIC_STATS_API` — the workers.dev URL from step 3 (no trailing slash)

   After that, every push that touches `worker/**` redeploys the worker
   automatically, and every site rebuild bakes the URL into the page.

## Endpoints

- `POST /visit` — bumps total + daily counters. Fire once per pageview.
- `POST /heartbeat?sid=<sessionId>` — sets a 45s-TTL key. Send every ~25s.
- `GET /stats` — `{ online, total, avg_per_hour, avg_per_day, avg_per_week, avg_per_month, since, days_tracked, generated_at }`

## Notes

- "Online" is computed by listing keys with prefix `live:`. Heartbeat
  TTL is 45s, so a tab that closes drops out within 45s of inactivity.
- Aggregates are refreshed at most every 90s (`stats:cache` key).
- All counters live in a single KV. Free tier gives 100k reads/day,
  which is plenty for this site's traffic.
