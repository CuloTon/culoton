/// <reference types="@cloudflare/workers-types" />
// CuloTon stats worker — pageviews, online presence, rolling averages.

interface Env {
  STATS_KV: KVNamespace;
  ALLOWED_ORIGIN?: string;
}

const HEARTBEAT_TTL = 45;
const STATS_CACHE_TTL = 90;
const SID_RE = /^[a-zA-Z0-9_-]{8,64}$/;

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

      return new Response('Not Found', { status: 404, headers });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      return new Response(`error: ${msg}`, { status: 500, headers });
    }
  },
};
