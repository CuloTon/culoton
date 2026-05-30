"""Shared heuristic: is a news headline low-value filler?

Used by fetch_news.py (skip before the rewrite API call) and
telegram_notify.py (never pick it as the hourly post).

RELAXED policy (2026-05-30, per user): favour freshness. Only the clearly
worthless stuff is filler:
  (a) the recurring exchange-listing micro-story ("TON/USDT pair on Binance"),
  (b) pure price-analysis / chartist phrasing ("price prediction", "dead cat
      bounce", "key resistance", "critical juncture"),
  (c) flat STABILITY recaps — "nothing happened, price is still $2"
      ("TON stabilizes at $2", "holds steady above $2", "trades near $1.95").

DIRECTIONAL moves with a reason are NOT filler — they carry news and freshness
("TON slides 11% as Bitcoin weakness drags crypto", "TON surges 20% on ETF
nod", "TON tests $2 support after unlock"). A little market noise is accepted
as the price of a livelier feed.
"""

from __future__ import annotations

import re

# A dollar price ($2, $1.95, $400M) or an explicit USD/USDT amount.
_PRICE = re.compile(r"\$\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|usdt|dollars?)\b", re.I)

# Flat / no-movement ("stability") language. Only THIS price-recap class is
# blocked now — directional moves (slides/surges/drops/rises) are allowed.
_STABILITY = re.compile(
    r"\b("
    r"stabiliz\w*|steady|steadies|stable|"
    r"hold(?:s|ing)?|hover\w*|"
    r"trad(?:es?|ing)\s+(?:flat|sideways|near|at|around|steady|range)|"
    r"flat|unchanged|sideways|range-?bound|consolidat\w*|rangebound|"
    r"steadies?\s+(?:near|at|around)|near\s+\$|at\s+\$|around\s+\$"
    r")\b",
    re.I,
)

# Pure price-analysis / prediction phrasing — low-value on its own.
_PRICE_ANALYSIS = re.compile(
    r"\bprice\s+(?:prediction|analysis|forecast|target|level|action|outlook|scenarios?)\b"
    r"|\bcan\s+\w+\s+(?:hit|reach|top)\s+\$"
    r"|\b(?:hit|reach|top)\s+\$\d",
    re.I,
)

# Pure technical-analysis chartist filler — no actual news, only chart talk.
_TA_FILLER = re.compile(
    r"\bdead\s+cat\b"
    r"|\bbounce\s+or\s+breakout\b"
    r"|\bprice\s+rally\b"
    r"|\b(?:critical|technical)\s+juncture\b"
    r"|\bcritical\s+technical\b"
    r"|\btrend\s+decision\b"
    r"|\bkey\s+resistance\b"
    r"|\bmarket\s+outlook\b",
    re.I,
)

# The recurring "TON/USDT pair on Binance" exchange-listing micro-story.
_LISTING = re.compile(
    r"(?:ton[\s/\-]?usdt|usdt\s+(?:trading\s+)?pair).*"
    r"(?:binance|listed|live|active|spot|trading|available|quoted)"
    r"|listed\s+on\s+binance"
    r"|now\s+(?:live|active|available|trading|listed)\s+on\s+binance"
    r"|trading\s+pair\s+(?:now\s+)?(?:live|active|remains|available|listed|quoted)",
    re.I,
)


def is_low_value_title(title: str) -> bool:
    """True only for clear filler — listing spam, pure chart-analysis, and
    flat stability recaps. Directional/catalyst moves pass."""
    t = (title or "").strip()
    if not t:
        return False
    if _LISTING.search(t):
        return True
    if _PRICE_ANALYSIS.search(t):
        return True
    if _TA_FILLER.search(t):
        return True
    if _PRICE.search(t) and _STABILITY.search(t):
        return True
    return False
