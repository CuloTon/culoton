/// <reference types="@cloudflare/workers-types" />
// CuloTon stats worker — pageviews, online presence, rolling averages.

interface Env {
  STATS_KV: KVNamespace;
  ALLOWED_ORIGIN?: string;
  POLL_IP_SALT?: string;
}

const HEARTBEAT_TTL = 45;
const STATS_CACHE_TTL = 90;
const SID_RE = /^[a-zA-Z0-9_-]{8,64}$/;

const POLL_VERSION = 'v1';
const POLL_CACHE_TTL = 30;
const POLL_Q1 = new Set(['keep', 'new']);
const POLL_Q2 = new Set(['tax', 'notax']);
const POLL_TAX_PCT = new Set([0, 3, 5, 8, 10, 15]);
const POLL_SPLIT = new Set(['100-0', '80-20', '60-40', '50-50', '40-60']);
const TICKER_RE = /^[A-Z0-9$_-]{2,12}$/;

function corsHeaders(req: Request, allowed: string): HeadersInit {
  const reqOrigin = req.headers.get('Origin') ?? '';
  let origin = '*';
  if (allowed && allowed !== '*') {
    const list = allowed.split(',').map((s) => s.trim()).filter(Boolean);
    origin = list.includes(reqOrigin) ? reqOrigin : list[0];
  }
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  };
}

function utcParts(d = new Date()) {
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(d.getUTCDate()).padStart(2, '0');
  const hh = String(d.getUTCHours()).padStart(2, '0');
  return { day: `${y}${m}${dd}`, hr: `${y}${m}${dd}${hh}`, iso: d.toISOString() };
}

async function inc(kv: KVNamespace, key: string, by = 1) {
  const cur = parseInt((await kv.get(key)) ?? '0', 10);
  await kv.put(key, String(cur + by));
}

async function listAll(kv: KVNamespace, prefix: string) {
  const out: { name: string }[] = [];
  let cursor: string | undefined;
  do {
    const res: KVNamespaceListResult<unknown, string> = await kv.list({ prefix, cursor, limit: 1000 });
    for (const k of res.keys) out.push({ name: k.name });
    if (res.list_complete) break;
    cursor = res.cursor;
  } while (cursor);
  return out;
}

async function sumValues(kv: KVNamespace, keys: { name: string }[]): Promise<number> {
  let total = 0;
  const BATCH = 50;
  for (let i = 0; i < keys.length; i += BATCH) {
    const slice = keys.slice(i, i + BATCH);
    const vals = await Promise.all(slice.map((k) => kv.get(k.name)));
    for (const v of vals) total += parseInt(v ?? '0', 10);
  }
  return total;
}

type StatsCore = {
  total: number;
  avg_per_hour: number;
  avg_per_day: number;
  avg_per_week: number;
  avg_per_month: number;
  days_tracked: number;
  since: string | null;
};

async function recomputeCore(env: Env): Promise<StatsCore> {
  const [totalRaw, started, dayKeys] = await Promise.all([
    env.STATS_KV.get('total'),
    env.STATS_KV.get('started_at'),
    listAll(env.STATS_KV, 'pv:day:'),
  ]);
  const total = parseInt(totalRaw ?? '0', 10);
  const sumDays = await sumValues(env.STATS_KV, dayKeys);
  const days = dayKeys.length || 1;
  const perDay = sumDays / days;
  return {
    total,
    avg_per_hour: Math.round(perDay / 24),
    avg_per_day: Math.round(perDay),
    avg_per_week: Math.round(perDay * 7),
    avg_per_month: Math.round(perDay * 30),
    days_tracked: dayKeys.length,
    since: started ?? null,
  };
}

async function readCached(env: Env): Promise<{ gen: number; data: StatsCore } | null> {
  const raw = await env.STATS_KV.get('stats:cache');
  if (!raw) return null;
  try {
    return JSON.parse(raw) as { gen: number; data: StatsCore };
  } catch {
    return null;
  }
}

async function storeCached(env: Env, data: StatsCore) {
  await env.STATS_KV.put(
    'stats:cache',
    JSON.stringify({ gen: Date.now(), data }),
    { expirationTtl: STATS_CACHE_TTL * 2 },
  );
}

type PollVote = {
  q1: 'keep' | 'new';
  q2: 'tax' | 'notax' | null;
  buy: number | null;
  sell: number | null;
  split: string | null;
  ticker: string | null;
  at: string;
};

type PollResults = {
  total: number;
  q1: Record<string, number>;
  q2: Record<string, number>;
  buy: Record<string, number>;
  sell: Record<string, number>;
  split: Record<string, number>;
  tickers: { ticker: string; count: number }[];
  generated_at: string;
};

async function hashIp(ip: string, salt: string): Promise<string> {
  const data = new TextEncoder().encode(`${salt}|${ip}`);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(digest))
    .slice(0, 16)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function getPollSalt(env: Env): Promise<string> {
  if (env.POLL_IP_SALT) return env.POLL_IP_SALT;
  const stored = await env.STATS_KV.get(`poll:${POLL_VERSION}:salt`);
  if (stored) return stored;
  const buf = new Uint8Array(32);
  crypto.getRandomValues(buf);
  const fresh = Array.from(buf).map((b) => b.toString(16).padStart(2, '0')).join('');
  await env.STATS_KV.put(`poll:${POLL_VERSION}:salt`, fresh);
  return fresh;
}

function normalizeTicker(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  let t = raw.trim().toUpperCase().replace(/^\$+/, '');
  if (!t) return null;
  if (t.length > 12) t = t.slice(0, 12);
  return TICKER_RE.test(t) ? t : null;
}

function validateVote(body: any): PollVote | { error: string } {
  if (!body || typeof body !== 'object') return { error: 'invalid body' };
  const q1 = String(body.q1 ?? '');
  if (!POLL_Q1.has(q1)) return { error: 'invalid q1' };

  let q2: 'tax' | 'notax' | null = null;
  let buy: number | null = null;
  let sell: number | null = null;
  let split: string | null = null;

  if (q1 === 'new') {
    const q2raw = String(body.q2 ?? '');
    if (!POLL_Q2.has(q2raw)) return { error: 'invalid q2' };
    q2 = q2raw as 'tax' | 'notax';
    if (q2 === 'tax') {
      const buyN = Number(body.buy);
      const sellN = Number(body.sell);
      if (!POLL_TAX_PCT.has(buyN)) return { error: 'invalid buy' };
      if (!POLL_TAX_PCT.has(sellN)) return { error: 'invalid sell' };
      const splitRaw = String(body.split ?? '');
      if (!POLL_SPLIT.has(splitRaw)) return { error: 'invalid split' };
      buy = buyN;
      sell = sellN;
      split = splitRaw;
    }
  }

  return {
    q1: q1 as 'keep' | 'new',
    q2,
    buy,
    sell,
    split,
    ticker: normalizeTicker(body.ticker),
    at: new Date().toISOString(),
  };
}

async function aggregatePoll(env: Env): Promise<PollResults> {
  const prefix = `poll:${POLL_VERSION}:vote:`;
  const keys = await listAll(env.STATS_KV, prefix);
  const q1: Record<string, number> = { keep: 0, new: 0 };
  const q2: Record<string, number> = { tax: 0, notax: 0 };
  const buy: Record<string, number> = {};
  const sell: Record<string, number> = {};
  const split: Record<string, number> = {};
  const tickers: Record<string, number> = {};

  const BATCH = 50;
  for (let i = 0; i < keys.length; i += BATCH) {
    const slice = keys.slice(i, i + BATCH);
    const vals = await Promise.all(slice.map((k) => env.STATS_KV.get(k.name)));
    for (const raw of vals) {
      if (!raw) continue;
      let v: PollVote;
      try {
        v = JSON.parse(raw) as PollVote;
      } catch {
        continue;
      }
      if (v.q1 && q1[v.q1] !== undefined) q1[v.q1]++;
      if (v.q2 && q2[v.q2] !== undefined) q2[v.q2]++;
      if (v.buy !== null && v.buy !== undefined) {
        const k = String(v.buy);
        buy[k] = (buy[k] ?? 0) + 1;
      }
      if (v.sell !== null && v.sell !== undefined) {
        const k = String(v.sell);
        sell[k] = (sell[k] ?? 0) + 1;
      }
      if (v.split) split[v.split] = (split[v.split] ?? 0) + 1;
      if (v.ticker) tickers[v.ticker] = (tickers[v.ticker] ?? 0) + 1;
    }
  }

  const tickerList = Object.entries(tickers)
    .map(([ticker, count]) => ({ ticker, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 30);

  return {
    total: keys.length,
    q1,
    q2,
    buy,
    sell,
    split,
    tickers: tickerList,
    generated_at: new Date().toISOString(),
  };
}

async function readPollCache(env: Env): Promise<{ gen: number; data: PollResults } | null> {
  const raw = await env.STATS_KV.get(`poll:${POLL_VERSION}:cache:results`);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as { gen: number; data: PollResults };
  } catch {
    return null;
  }
}

async function storePollCache(env: Env, data: PollResults) {
  await env.STATS_KV.put(
    `poll:${POLL_VERSION}:cache:results`,
    JSON.stringify({ gen: Date.now(), data }),
    { expirationTtl: POLL_CACHE_TTL * 2 },
  );
}

async function invalidatePollCache(env: Env) {
  await env.STATS_KV.delete(`poll:${POLL_VERSION}:cache:results`);
}

// === Token registry — feed of jettons launched via /launch ===
const TOK_VERSION = 'v1';
const TOK_LIST_CACHE_TTL = 30;
const TOK_MAX_LIST = 300;
const TON_ADDR_RE = /^[A-Za-z0-9_-]{48}$/; // user-friendly base64url TON address
const TOK_NET = new Set(['testnet', 'mainnet']);

type TokenEntry = {
  minter: string;
  network: 'testnet' | 'mainnet';
  name: string;
  symbol: string;
  decimals: number;
  image: string;
  owner: string;
  supply: string;
  at: string;
};

function clampStr(v: unknown, max: number): string {
  if (typeof v !== 'string') return '';
  return v.trim().slice(0, max);
}

function validateToken(body: any): TokenEntry | { error: string } {
  if (!body || typeof body !== 'object') return { error: 'invalid body' };
  const minter = clampStr(body.minter, 60);
  if (!TON_ADDR_RE.test(minter)) return { error: 'invalid minter' };
  const network = String(body.network ?? 'testnet');
  if (!TOK_NET.has(network)) return { error: 'invalid network' };
  const name = clampStr(body.name, 64);
  const symbol = clampStr(body.symbol, 16);
  if (!name || !symbol) return { error: 'missing name/symbol' };
  let decimals = Number(body.decimals);
  if (!Number.isInteger(decimals) || decimals < 0 || decimals > 30) decimals = 9;
  const imageRaw = clampStr(body.image, 400);
  const image = /^https?:\/\/|^ipfs:\/\//.test(imageRaw) ? imageRaw : '';
  const ownerRaw = clampStr(body.owner, 60);
  const owner = TON_ADDR_RE.test(ownerRaw) ? ownerRaw : '';
  const supply = clampStr(body.supply, 40).replace(/[^0-9]/g, '');
  return {
    minter,
    network: network as 'testnet' | 'mainnet',
    name,
    symbol,
    decimals,
    image,
    owner,
    supply,
    at: new Date().toISOString(),
  };
}

async function listTokens(env: Env, network: string): Promise<TokenEntry[]> {
  const keys = await listAll(env.STATS_KV, `tok:${TOK_VERSION}:${network}:`);
  const out: TokenEntry[] = [];
  const BATCH = 50;
  for (let i = 0; i < keys.length; i += BATCH) {
    const slice = keys.slice(i, i + BATCH);
    const vals = await Promise.all(slice.map((k) => env.STATS_KV.get(k.name)));
    for (const raw of vals) {
      if (!raw) continue;
      try {
        out.push(JSON.parse(raw) as TokenEntry);
      } catch {
        /* skip */
      }
    }
  }
  out.sort((a, b) => (a.at < b.at ? 1 : a.at > b.at ? -1 : 0));
  return out.slice(0, TOK_MAX_LIST);
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const allowed = env.ALLOWED_ORIGIN ?? '*';
    const headers = corsHeaders(req, allowed);

    if (req.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers });
    }

    try {
      if (url.pathname === '/visit' && req.method === 'POST') {
        const { day, hr, iso } = utcParts();
        await Promise.all([
          inc(env.STATS_KV, 'total'),
          inc(env.STATS_KV, `pv:day:${day}`),
          inc(env.STATS_KV, `pv:hr:${hr}`),
        ]);
        const started = await env.STATS_KV.get('started_at');
        if (!started) await env.STATS_KV.put('started_at', iso);
        return new Response(null, { status: 204, headers });
      }

      if (url.pathname === '/heartbeat' && req.method === 'POST') {
        const sid = url.searchParams.get('sid') ?? '';
        if (!SID_RE.test(sid)) {
          return new Response('bad sid', { status: 400, headers });
        }
        await env.STATS_KV.put(`live:${sid}`, '1', { expirationTtl: HEARTBEAT_TTL });
        return new Response(null, { status: 204, headers });
      }

      if (url.pathname === '/stats' && req.method === 'GET') {
        const liveList = await env.STATS_KV.list({ prefix: 'live:', limit: 1000 });
        const online = liveList.keys.length;

        let cached = await readCached(env);
        const ageSec = cached ? (Date.now() - cached.gen) / 1000 : Infinity;
        let data: StatsCore;
        if (cached && ageSec < STATS_CACHE_TTL) {
          data = cached.data;
        } else {
          data = await recomputeCore(env);
          await storeCached(env, data);
        }

        const body = { online, ...data, generated_at: new Date().toISOString() };
        return new Response(JSON.stringify(body), {
          status: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'public, max-age=30',
          },
        });
      }

      if (url.pathname === '/poll/vote' && req.method === 'POST') {
        const ip = req.headers.get('CF-Connecting-IP') ?? '0.0.0.0';
        const salt = await getPollSalt(env);
        const ipHash = await hashIp(ip, salt);
        const voteKey = `poll:${POLL_VERSION}:vote:${ipHash}`;

        let body: any;
        try {
          body = await req.json();
        } catch {
          return new Response(JSON.stringify({ error: 'invalid json' }), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        const parsed = validateVote(body);
        if ('error' in parsed) {
          return new Response(JSON.stringify(parsed), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }

        const existing = await env.STATS_KV.get(voteKey);
        if (existing) {
          const results = await aggregatePoll(env);
          await storePollCache(env, results);
          return new Response(JSON.stringify({ duplicate: true, results }), {
            status: 409,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }

        await env.STATS_KV.put(voteKey, JSON.stringify(parsed));
        await invalidatePollCache(env);
        const results = await aggregatePoll(env);
        await storePollCache(env, results);
        return new Response(JSON.stringify({ ok: true, results }), {
          status: 200,
          headers: { ...headers, 'Content-Type': 'application/json' },
        });
      }

      if (url.pathname === '/poll/results' && req.method === 'GET') {
        const cached = await readPollCache(env);
        const ageSec = cached ? (Date.now() - cached.gen) / 1000 : Infinity;
        let data: PollResults;
        if (cached && ageSec < POLL_CACHE_TTL) {
          data = cached.data;
        } else {
          data = await aggregatePoll(env);
          await storePollCache(env, data);
        }
        return new Response(JSON.stringify(data), {
          status: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'public, max-age=15',
          },
        });
      }

      if (url.pathname === '/poll/check' && req.method === 'GET') {
        const ip = req.headers.get('CF-Connecting-IP') ?? '0.0.0.0';
        const salt = await getPollSalt(env);
        const ipHash = await hashIp(ip, salt);
        const existing = await env.STATS_KV.get(`poll:${POLL_VERSION}:vote:${ipHash}`);
        return new Response(JSON.stringify({ voted: !!existing }), {
          status: 200,
          headers: { ...headers, 'Content-Type': 'application/json' },
        });
      }

      if (url.pathname === '/tokens/register' && req.method === 'POST') {
        let body: any;
        try {
          body = await req.json();
        } catch {
          return new Response(JSON.stringify({ error: 'invalid json' }), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        const parsed = validateToken(body);
        if ('error' in parsed) {
          return new Response(JSON.stringify(parsed), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        const key = `tok:${TOK_VERSION}:${parsed.network}:${parsed.minter}`;
        const existing = await env.STATS_KV.get(key);
        if (!existing) {
          await env.STATS_KV.put(key, JSON.stringify(parsed));
          await env.STATS_KV.delete(`tok:${TOK_VERSION}:cache:${parsed.network}`);
        }
        return new Response(JSON.stringify({ ok: true, duplicate: !!existing }), {
          status: 200,
          headers: { ...headers, 'Content-Type': 'application/json' },
        });
      }

      if (url.pathname === '/tokens/list' && req.method === 'GET') {
        const netParam = url.searchParams.get('network') ?? 'testnet';
        const network = TOK_NET.has(netParam) ? netParam : 'testnet';
        const cacheKey = `tok:${TOK_VERSION}:cache:${network}`;
        const cachedRaw = await env.STATS_KV.get(cacheKey);
        let tokens: TokenEntry[] | null = null;
        if (cachedRaw) {
          try {
            const c = JSON.parse(cachedRaw) as { gen: number; tokens: TokenEntry[] };
            if ((Date.now() - c.gen) / 1000 < TOK_LIST_CACHE_TTL) tokens = c.tokens;
          } catch {
            /* recompute */
          }
        }
        if (!tokens) {
          tokens = await listTokens(env, network);
          await env.STATS_KV.put(
            cacheKey,
            JSON.stringify({ gen: Date.now(), tokens }),
            { expirationTtl: TOK_LIST_CACHE_TTL * 2 },
          );
        }
        return new Response(JSON.stringify({ network, count: tokens.length, tokens }), {
          status: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'public, max-age=15',
          },
        });
      }

      return new Response('Not Found', { status: 404, headers });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      return new Response(`error: ${msg}`, { status: 500, headers });
    }
  },
};
