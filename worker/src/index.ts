/// <reference types="@cloudflare/workers-types" />
// CuloTon stats worker — pageviews, online presence, rolling averages.

interface Env {
  STATS_KV: KVNamespace;
  ALLOWED_ORIGIN?: string;
  POLL_IP_SALT?: string;
  // Secret for the admin-curated token listing board (/listing/*).
  // Set via: wrangler secret put ADMIN_KEY
  ADMIN_KEY?: string;
  // Telegram bot creds — used to announce newly listed tokens.
  TELEGRAM_BOT_TOKEN?: string;
  TELEGRAM_CHAT_ID?: string;
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
    'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Key',
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
  website: string;
  telegram: string;
  x: string;
  at: string;
};

function clampStr(v: unknown, max: number): string {
  if (typeof v !== 'string') return '';
  return v.trim().slice(0, max);
}

// Optional social/website link — keep only well-formed http(s) URLs.
function sanUrl(v: unknown, max = 200): string {
  const s = clampStr(v, max);
  return /^https?:\/\//i.test(s) ? s : '';
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
  const website = sanUrl(body.website);
  const telegram = sanUrl(body.telegram);
  const x = sanUrl(body.x);
  return {
    minter,
    network: network as 'testnet' | 'mainnet',
    name,
    symbol,
    decimals,
    image,
    owner,
    supply,
    website,
    telegram,
    x,
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

// === Admin-curated listing board — tokens picked by hand (/token page) ===
// Distinct from the launch feed above: these are arbitrary TON jettons the
// admin lists by contract address; market data (chart/mcap/volume) is fetched
// client-side from GeckoTerminal/DexScreener. Adding is gated by ADMIN_KEY so
// the same endpoint can later be reused behind a paid (TON-fee) submission.
const LIST_VERSION = 'v1';
const LIST_CACHE_TTL = 30;
const LIST_MAX = 200;

type Listing = {
  ca: string;
  label: string;
  note: string;
  telegram: string;
  x: string;
  buy: string;
  sell: string;
  holders: string;
  network: 'testnet' | 'mainnet';
  at: string;
};

// Tax percentage as entered by the admin (TON has no standard on-chain tax
// field, so these are manual). Keep digits + one dot, clamp 0..100, drop the
// rest; return '' when empty/invalid.
function taxPct(v: unknown): string {
  if (typeof v !== 'string') return '';
  const cleaned = v.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
  if (!cleaned || cleaned === '.') return '';
  const num = parseFloat(cleaned);
  if (!isFinite(num) || num < 0 || num > 100) return '';
  return String(num);
}

// Constant-time-ish comparison so a wrong key can't be timed out character by character.
function adminOK(req: Request, env: Env): boolean {
  const got = req.headers.get('X-Admin-Key') ?? '';
  const want = env.ADMIN_KEY ?? '';
  if (!want || got.length !== want.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= got.charCodeAt(i) ^ want.charCodeAt(i);
  return diff === 0;
}

function validateListing(body: any): Listing | { error: string } {
  if (!body || typeof body !== 'object') return { error: 'invalid body' };
  const ca = clampStr(body.ca, 60);
  if (!TON_ADDR_RE.test(ca)) return { error: 'invalid ca' };
  const network = String(body.network ?? 'mainnet');
  if (!TOK_NET.has(network)) return { error: 'invalid network' };
  return {
    ca,
    label: clampStr(body.label, 64),
    note: clampStr(body.note, 200),
    telegram: sanUrl(body.telegram),
    x: sanUrl(body.x),
    buy: taxPct(body.buy),
    sell: taxPct(body.sell),
    holders: taxPct(body.holders),
    network: network as 'testnet' | 'mainnet',
    at: new Date().toISOString(),
  };
}

async function listListings(env: Env, network: string): Promise<Listing[]> {
  const keys = await listAll(env.STATS_KV, `list:${LIST_VERSION}:${network}:`);
  const out: Listing[] = [];
  const BATCH = 50;
  for (let i = 0; i < keys.length; i += BATCH) {
    const slice = keys.slice(i, i + BATCH);
    const vals = await Promise.all(slice.map((k) => env.STATS_KV.get(k.name)));
    for (const raw of vals) {
      if (!raw) continue;
      try {
        out.push(JSON.parse(raw) as Listing);
      } catch {
        /* skip */
      }
    }
  }
  out.sort((a, b) => (a.at < b.at ? 1 : a.at > b.at ? -1 : 0));
  return out.slice(0, LIST_MAX);
}

// Announce a newly listed token to Telegram, trilingual (RU/EN/PL) + link.
// Best-effort: any failure is swallowed so it never blocks the listing.
async function announceListing(env: Env, t: Listing): Promise<void> {
  const token = env.TELEGRAM_BOT_TOKEN;
  const chat = env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return;
  let name = t.label || '';
  let symbol = '';
  try {
    const r = await fetch('https://tonapi.io/v2/jettons/' + encodeURIComponent(t.ca));
    if (r.ok) {
      const j: any = await r.json();
      const m = j.metadata || {};
      name = m.name || name;
      symbol = (m.symbol || '').replace(/^\$+/, '');
    }
  } catch {
    /* ignore — fall back to label */
  }
  const title = (name || 'New token') + (symbol ? ' ($' + symbol + ')' : '');
  const link = 'https://brainrot-ton.fun/token/view?ca=' + encodeURIComponent(t.ca);
  const taxParts: string[] = [];
  if (t.buy) taxParts.push('Buy ' + t.buy + '%');
  if (t.sell) taxParts.push('Sell ' + t.sell + '%');
  if (t.holders) taxParts.push('Holders ' + t.holders + '%');
  const taxLine = taxParts.length ? '💸 ' + taxParts.join(' · ') + '\n' : '';
  const tgLine = t.telegram ? '💬 ' + t.telegram + '\n' : '';
  const text =
    '🆕 ' + title + '\n' + taxLine + tgLine + '\n' +
    '🇷🇺 Новый токен на TAX-доске BRAINROT\n' +
    '🇬🇧 New token on the BRAINROT TAX board\n' +
    '🇵🇱 Nowy token na tablicy TAX BRAINROT\n\n' +
    '📈 ' + link;
  try {
    await fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chat, text, disable_web_page_preview: false }),
    });
  } catch {
    /* ignore */
  }
}

// ===================== BLOG (BRTP economy) =====================
// Community blog: email+password accounts, multilingual articles, one upvote
// per user per article. Author +10 BRTP/point, voter +1 BRTP/vote (cap 20/day).
// BRTP is an off-chain ledger settled manually to each user's TON address.
const BLOG_VER = 'v1';
const BLOG_LANGS = new Set(['en', 'ru', 'pl', 'de', 'es', 'uk']);
const BLOG_AUTHOR_REWARD = 10;
const BLOG_VOTER_REWARD = 1;
const BLOG_DAILY_VOTE_CAP = 20;
const SESSION_TTL = 60 * 60 * 24 * 30; // 30 days
const LOGIN_RE = /^[A-Za-z0-9_-]{3,24}$/;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

type BUser = {
  uid: string; login: string; email: string; avatar: string; ton: string;
  salt: string; hash: string; earned: number; paid: number; banned: boolean; at: string;
};
type Article = {
  aid: string; uid: string; authorLogin: string; authorAvatar: string;
  lang: string; title: string; body: string; points: number; demo: boolean; at: string;
};

function hex(buf: ArrayBuffer): string {
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
}
function randHex(n: number): string {
  const b = new Uint8Array(n); crypto.getRandomValues(b);
  return Array.from(b).map((x) => x.toString(16).padStart(2, '0')).join('');
}
async function pbkdf2(pw: string, saltHex: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveBits']);
  const salt = Uint8Array.from((saltHex.match(/../g) || []).map((h) => parseInt(h, 16)));
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' }, key, 256);
  return hex(bits);
}
function jsonRes(headers: HeadersInit, body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { ...headers, 'Content-Type': 'application/json; charset=utf-8' } });
}
async function blogUser(req: Request, env: Env): Promise<BUser | null> {
  const auth = req.headers.get('Authorization') || '';
  const tok = auth.replace(/^Bearer\s+/i, '').trim();
  if (!tok) return null;
  const uid = await env.STATS_KV.get(`bsess:${BLOG_VER}:${tok}`);
  if (!uid) return null;
  const raw = await env.STATS_KV.get(`buser:${BLOG_VER}:${uid}`);
  if (!raw) return null;
  try { return JSON.parse(raw) as BUser; } catch { return null; }
}
function pubUser(u: BUser) {
  return { uid: u.uid, login: u.login, email: u.email, avatar: u.avatar, ton: u.ton, earned: u.earned, paid: u.paid, unpaid: u.earned - u.paid };
}
function pubArticle(a: Article, full = false) {
  const o: any = { aid: a.aid, authorLogin: a.authorLogin, authorAvatar: a.authorAvatar, lang: a.lang, title: a.title, points: a.points, brtp: a.points * BLOG_AUTHOR_REWARD, demo: a.demo, at: a.at };
  o.body = full ? a.body : a.body.slice(0, 200);
  return o;
}
async function listArticles(env: Env): Promise<Article[]> {
  const keys = await listAll(env.STATS_KV, `bart:${BLOG_VER}:`);
  const out: Article[] = [];
  const BATCH = 50;
  for (let i = 0; i < keys.length; i += BATCH) {
    const vals = await Promise.all(keys.slice(i, i + BATCH).map((k) => env.STATS_KV.get(k.name)));
    for (const raw of vals) { if (!raw) continue; try { out.push(JSON.parse(raw) as Article); } catch { /* skip */ } }
  }
  return out;
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

      if (url.pathname === '/listing/add' && req.method === 'POST') {
        if (!adminOK(req, env)) {
          return new Response(JSON.stringify({ error: 'unauthorized' }), {
            status: 401,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        let body: any;
        try {
          body = await req.json();
        } catch {
          return new Response(JSON.stringify({ error: 'invalid json' }), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        const parsed = validateListing(body);
        if ('error' in parsed) {
          return new Response(JSON.stringify(parsed), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        const key = `list:${LIST_VERSION}:${parsed.network}:${parsed.ca}`;
        const existing = await env.STATS_KV.get(key);
        await env.STATS_KV.put(key, JSON.stringify(parsed));
        await env.STATS_KV.delete(`list:${LIST_VERSION}:cache:${parsed.network}`);
        if (!existing) await announceListing(env, parsed);
        return new Response(JSON.stringify({ ok: true, duplicate: !!existing }), {
          status: 200,
          headers: { ...headers, 'Content-Type': 'application/json' },
        });
      }

      if (url.pathname === '/listing/remove' && req.method === 'POST') {
        if (!adminOK(req, env)) {
          return new Response(JSON.stringify({ error: 'unauthorized' }), {
            status: 401,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        let body: any;
        try {
          body = await req.json();
        } catch {
          return new Response(JSON.stringify({ error: 'invalid json' }), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        const ca = clampStr(body?.ca, 60);
        const netRaw = String(body?.network ?? 'mainnet');
        if (!TON_ADDR_RE.test(ca) || !TOK_NET.has(netRaw)) {
          return new Response(JSON.stringify({ error: 'invalid ca/network' }), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' },
          });
        }
        await env.STATS_KV.delete(`list:${LIST_VERSION}:${netRaw}:${ca}`);
        await env.STATS_KV.delete(`list:${LIST_VERSION}:cache:${netRaw}`);
        return new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: { ...headers, 'Content-Type': 'application/json' },
        });
      }

      if (url.pathname === '/listing/list' && req.method === 'GET') {
        const netParam = url.searchParams.get('network') ?? 'mainnet';
        const network = TOK_NET.has(netParam) ? netParam : 'mainnet';
        const cacheKey = `list:${LIST_VERSION}:cache:${network}`;
        const cachedRaw = await env.STATS_KV.get(cacheKey);
        let listings: Listing[] | null = null;
        if (cachedRaw) {
          try {
            const c = JSON.parse(cachedRaw) as { gen: number; listings: Listing[] };
            if ((Date.now() - c.gen) / 1000 < LIST_CACHE_TTL) listings = c.listings;
          } catch {
            /* recompute */
          }
        }
        if (!listings) {
          listings = await listListings(env, network);
          await env.STATS_KV.put(
            cacheKey,
            JSON.stringify({ gen: Date.now(), listings }),
            { expirationTtl: LIST_CACHE_TTL * 2 },
          );
        }
        return new Response(JSON.stringify({ network, count: listings.length, listings }), {
          status: 200,
          headers: {
            ...headers,
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'public, max-age=15',
          },
        });
      }

      // ---------- BLOG ----------
      if (url.pathname === '/blog/register' && req.method === 'POST') {
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        const login = clampStr(b.login, 24);
        const email = clampStr(b.email, 120).toLowerCase();
        const password = typeof b.password === 'string' ? b.password : '';
        const avatar = sanUrl(b.avatar, 400);
        const ton = clampStr(b.ton, 60);
        if (!LOGIN_RE.test(login)) return jsonRes(headers, { error: 'login must be 3-24 chars (a-z, 0-9, _ -)' }, 400);
        if (!EMAIL_RE.test(email)) return jsonRes(headers, { error: 'invalid email' }, 400);
        if (password.length < 6) return jsonRes(headers, { error: 'password too short (min 6)' }, 400);
        if (!TON_ADDR_RE.test(ton)) return jsonRes(headers, { error: 'invalid TON address' }, 400);
        if (await env.STATS_KV.get(`bemail:${BLOG_VER}:${email}`)) return jsonRes(headers, { error: 'email already registered' }, 409);
        if (await env.STATS_KV.get(`blogin:${BLOG_VER}:${login.toLowerCase()}`)) return jsonRes(headers, { error: 'login already taken' }, 409);
        const uid = randHex(8), salt = randHex(16), hash = await pbkdf2(password, salt);
        const u: BUser = { uid, login, email, avatar, ton, salt, hash, earned: 0, paid: 0, banned: false, at: new Date().toISOString() };
        await env.STATS_KV.put(`buser:${BLOG_VER}:${uid}`, JSON.stringify(u));
        await env.STATS_KV.put(`bemail:${BLOG_VER}:${email}`, uid);
        await env.STATS_KV.put(`blogin:${BLOG_VER}:${login.toLowerCase()}`, uid);
        const tok = randHex(24); await env.STATS_KV.put(`bsess:${BLOG_VER}:${tok}`, uid, { expirationTtl: SESSION_TTL });
        return jsonRes(headers, { ok: true, token: tok, user: pubUser(u) });
      }
      if (url.pathname === '/blog/login' && req.method === 'POST') {
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        const email = clampStr(b.email, 120).toLowerCase();
        const password = typeof b.password === 'string' ? b.password : '';
        const uid = await env.STATS_KV.get(`bemail:${BLOG_VER}:${email}`);
        if (!uid) return jsonRes(headers, { error: 'wrong email or password' }, 401);
        const raw = await env.STATS_KV.get(`buser:${BLOG_VER}:${uid}`);
        if (!raw) return jsonRes(headers, { error: 'wrong email or password' }, 401);
        const u = JSON.parse(raw) as BUser;
        if (u.banned) return jsonRes(headers, { error: 'account banned' }, 403);
        if ((await pbkdf2(password, u.salt)) !== u.hash) return jsonRes(headers, { error: 'wrong email or password' }, 401);
        const tok = randHex(24); await env.STATS_KV.put(`bsess:${BLOG_VER}:${tok}`, uid, { expirationTtl: SESSION_TTL });
        return jsonRes(headers, { ok: true, token: tok, user: pubUser(u) });
      }
      if (url.pathname === '/blog/me' && req.method === 'GET') {
        const u = await blogUser(req, env); if (!u) return jsonRes(headers, { error: 'unauthorized' }, 401);
        return jsonRes(headers, { user: pubUser(u) });
      }
      if (url.pathname === '/blog/account' && req.method === 'POST') {
        const u = await blogUser(req, env); if (!u) return jsonRes(headers, { error: 'unauthorized' }, 401);
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        if (b.avatar !== undefined) u.avatar = sanUrl(b.avatar, 400);
        if (b.ton !== undefined) { const t = clampStr(b.ton, 60); if (t && !TON_ADDR_RE.test(t)) return jsonRes(headers, { error: 'invalid TON address' }, 400); u.ton = t; }
        await env.STATS_KV.put(`buser:${BLOG_VER}:${u.uid}`, JSON.stringify(u));
        return jsonRes(headers, { ok: true, user: pubUser(u) });
      }
      if (url.pathname === '/blog/articles' && req.method === 'GET') {
        const lang = url.searchParams.get('lang') || '';
        let arts = await listArticles(env);
        if (BLOG_LANGS.has(lang)) arts = arts.filter((a) => a.lang === lang);
        arts.sort((x, y) => (y.points - x.points) || (x.at < y.at ? 1 : x.at > y.at ? -1 : 0));
        return jsonRes(headers, { count: arts.length, articles: arts.slice(0, 300).map((a) => pubArticle(a, false)) });
      }
      if (url.pathname === '/blog/article' && req.method === 'GET') {
        const id = clampStr(url.searchParams.get('id'), 32);
        const raw = await env.STATS_KV.get(`bart:${BLOG_VER}:${id}`);
        if (!raw) return jsonRes(headers, { error: 'not found' }, 404);
        const a = JSON.parse(raw) as Article;
        const u = await blogUser(req, env);
        const voted = u ? !!(await env.STATS_KV.get(`bvote:${BLOG_VER}:${id}:${u.uid}`)) : false;
        return jsonRes(headers, { article: pubArticle(a, true), voted, mine: !!(u && u.uid === a.uid) });
      }
      if (url.pathname === '/blog/article' && req.method === 'POST') {
        const u = await blogUser(req, env); if (!u) return jsonRes(headers, { error: 'unauthorized' }, 401);
        if (u.banned) return jsonRes(headers, { error: 'banned' }, 403);
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        const lang = String(b.lang || 'en'); if (!BLOG_LANGS.has(lang)) return jsonRes(headers, { error: 'invalid language' }, 400);
        const title = clampStr(b.title, 200), body = clampStr(b.body, 20000);
        if (!title || body.length < 10) return jsonRes(headers, { error: 'title and body (min 10 chars) required' }, 400);
        const aid = randHex(8);
        const a: Article = { aid, uid: u.uid, authorLogin: u.login, authorAvatar: u.avatar, lang, title, body, points: 0, demo: false, at: new Date().toISOString() };
        await env.STATS_KV.put(`bart:${BLOG_VER}:${aid}`, JSON.stringify(a));
        return jsonRes(headers, { ok: true, aid });
      }
      if (url.pathname === '/blog/vote' && req.method === 'POST') {
        const u = await blogUser(req, env); if (!u) return jsonRes(headers, { error: 'unauthorized' }, 401);
        if (u.banned) return jsonRes(headers, { error: 'banned' }, 403);
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        const aid = clampStr(b.aid, 32);
        const k = `bart:${BLOG_VER}:${aid}`, raw = await env.STATS_KV.get(k);
        if (!raw) return jsonRes(headers, { error: 'article not found' }, 404);
        const a = JSON.parse(raw) as Article;
        if (a.uid === u.uid) return jsonRes(headers, { error: 'cannot vote your own article' }, 403);
        const vkey = `bvote:${BLOG_VER}:${aid}:${u.uid}`;
        if (await env.STATS_KV.get(vkey)) return jsonRes(headers, { error: 'already voted', points: a.points }, 409);
        const day = utcParts().day, dkey = `bvday:${BLOG_VER}:${u.uid}:${day}`;
        const cnt = parseInt((await env.STATS_KV.get(dkey)) || '0', 10);
        if (cnt >= BLOG_DAILY_VOTE_CAP) return jsonRes(headers, { error: 'daily vote limit reached (' + BLOG_DAILY_VOTE_CAP + ')' }, 429);
        await env.STATS_KV.put(vkey, '1');
        await env.STATS_KV.put(dkey, String(cnt + 1), { expirationTtl: 60 * 60 * 48 });
        a.points += 1;
        await env.STATS_KV.put(k, JSON.stringify(a));
        if (!a.demo) {
          const araw = await env.STATS_KV.get(`buser:${BLOG_VER}:${a.uid}`);
          if (araw) { const au = JSON.parse(araw) as BUser; au.earned += BLOG_AUTHOR_REWARD; await env.STATS_KV.put(`buser:${BLOG_VER}:${a.uid}`, JSON.stringify(au)); }
          u.earned += BLOG_VOTER_REWARD; await env.STATS_KV.put(`buser:${BLOG_VER}:${u.uid}`, JSON.stringify(u));
        }
        return jsonRes(headers, { ok: true, points: a.points, brtp: a.points * BLOG_AUTHOR_REWARD, earnedVoter: !a.demo ? BLOG_VOTER_REWARD : 0 });
      }
      if (url.pathname === '/blog/admin/users' && req.method === 'GET') {
        if (!adminOK(req, env)) return jsonRes(headers, { error: 'unauthorized' }, 401);
        const keys = await listAll(env.STATS_KV, `buser:${BLOG_VER}:`);
        const out: any[] = []; const BATCH = 50;
        for (let i = 0; i < keys.length; i += BATCH) {
          const vals = await Promise.all(keys.slice(i, i + BATCH).map((kk) => env.STATS_KV.get(kk.name)));
          for (const raw of vals) { if (!raw) continue; try { const u = JSON.parse(raw) as BUser; out.push({ uid: u.uid, login: u.login, email: u.email, ton: u.ton, earned: u.earned, paid: u.paid, unpaid: u.earned - u.paid, banned: u.banned, at: u.at }); } catch { /* skip */ } }
        }
        out.sort((a, b) => (b.earned - b.paid) - (a.earned - a.paid));
        return jsonRes(headers, { count: out.length, users: out });
      }
      if (url.pathname === '/blog/admin/payout' && req.method === 'POST') {
        if (!adminOK(req, env)) return jsonRes(headers, { error: 'unauthorized' }, 401);
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        const uid = clampStr(b.uid, 32), amount = Number(b.amount);
        if (!isFinite(amount) || amount < 0) return jsonRes(headers, { error: 'bad amount' }, 400);
        const raw = await env.STATS_KV.get(`buser:${BLOG_VER}:${uid}`);
        if (!raw) return jsonRes(headers, { error: 'user not found' }, 404);
        const u = JSON.parse(raw) as BUser; u.paid += amount;
        await env.STATS_KV.put(`buser:${BLOG_VER}:${uid}`, JSON.stringify(u));
        return jsonRes(headers, { ok: true, user: pubUser(u) });
      }
      if (url.pathname === '/blog/admin/article' && req.method === 'POST') {
        if (!adminOK(req, env)) return jsonRes(headers, { error: 'unauthorized' }, 401);
        let b: any; try { b = await req.json(); } catch { return jsonRes(headers, { error: 'invalid json' }, 400); }
        const aid = clampStr(b.aid, 32), action = String(b.action || '');
        const k = `bart:${BLOG_VER}:${aid}`, raw = await env.STATS_KV.get(k);
        if (!raw) return jsonRes(headers, { error: 'not found' }, 404);
        const a = JSON.parse(raw) as Article;
        if (action === 'delete') { await env.STATS_KV.delete(k); return jsonRes(headers, { ok: true, deleted: true }); }
        if (action === 'demo') a.demo = true; else if (action === 'undemo') a.demo = false; else return jsonRes(headers, { error: 'bad action' }, 400);
        await env.STATS_KV.put(k, JSON.stringify(a));
        return jsonRes(headers, { ok: true });
      }

      return new Response('Not Found', { status: 404, headers });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      return new Response(`error: ${msg}`, { status: 500, headers });
    }
  },
};
