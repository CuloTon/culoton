// Collapse near-identical headlines (the same story re-reported by several
// outlets — e.g. "Acton Toolchain Debuts on TON…" and "Acton Toolchain
// Arrives on TON…") so listings don't show three rows of essentially the
// same news. Keeps the first occurrence — callers pass entries newest-first.
//
// The same heuristic lives in scripts/tg_bot_interact.py (`dedup_news`) for
// the /news Telegram command; keep the two in rough sync.

// Words too generic to count toward "two headlines are the same story".
const STOPWORDS = new Set([
  'a', 'an', 'the', 'on', 'in', 'of', 'to', 'for', 'and', 'as', 'at',
  'with', 'by', 'amid', 'this', 'that', 'from', 'is', 'are', 'be', 'its',
  'it', 'after', 'over', 'into', 'than', 'but', 'or', 'up', 'down', 'out',
]);

/** Normalised content words of a headline (lowercased, depluralised, stopwords dropped). */
function titleTokens(title: string): Set<string> {
  const out = new Set<string>();
  for (let tok of (title || '').toLowerCase().split(/[^0-9a-z]+/)) {
    if (!tok || STOPWORDS.has(tok)) continue;
    if (tok.length > 3 && tok.endsWith('s')) tok = tok.slice(0, -1);
    out.add(tok);
  }
  return out;
}

function nearDuplicate(a: Set<string>, b: Set<string>, threshold = 0.6): boolean {
  if (a.size === 0 || b.size === 0) return false;
  let inter = 0;
  for (const t of a) if (b.has(t)) inter++;
  return inter / Math.min(a.size, b.size) >= threshold;
}

/** Drop near-duplicate headlines, keeping the first occurrence. */
export function dedupeByTitle<T extends { data: { title: string } }>(entries: T[]): T[] {
  const kept: T[] = [];
  const seen: Set<string>[] = [];
  for (const entry of entries) {
    const toks = titleTokens(entry.data.title);
    if (seen.some((prev) => nearDuplicate(toks, prev))) continue;
    kept.push(entry);
    seen.push(toks);
  }
  return kept;
}
