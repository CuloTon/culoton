"""Shared heuristic: is a news headline low-value "market noise" — i.e.
price-recap / market-mood filler that should never dominate the channel or
the site?

Two scripts use it:
  - fetch_news.py      — skip before spending an API call to rewrite it
  - telegram_notify.py — never pick it as the hourly channel post

A headline is flagged when it is dominated by market-action language rather
than actual news:
  (a) the recurring exchange-listing micro-story ("TON/USDT pair on Binance"),
  (b) price-analysis / prediction phrasing ("Can Toncoin hit $10", "price
      prediction"),
  (c) a price OR percentage move paired with a movement/level verb
      ("TON tests $2 support", "Toncoin slides 11%", "stabilizes at $2"),
  (d) pure market-mood phrasing ("broader market pullback", "downward
      pressure", "bear market").

We bias toward KEEPING substantive stories: a price/percent that merely
provides context, without market-action framing, passes — e.g.
"Venture firms back Toncoin with $400M", "SuperEarn offers up to 27% APR",
"Telegram brings TON wallet to 87M users".
"""

from __future__ import annotations

import re

# A dollar price ($2, $1.95, $400M) or an explicit USD/USDT amount.
_PRICE = re.compile(r"\$\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|usdt|dollars?)\b", re.I)

# A percentage figure (11%, 5.4 %).
_PCT = re.compile(r"\b\d+(?:\.\d+)?\s*%")

# Movement / price-level verbs and nouns that mark a market recap. These only
# flag a headline when a price or percentage is also present (tier c).
_MOVE = re.compile(
    r"\b("
    r"stabiliz\w*|steady|steadies|hold(?:s|ing)?|hover\w*|"
    r"trad(?:es?|ing)\s+(?:near|at|around|above|below)|"
    r"edges?|dips?|dipped|slips?|slipped|slid\w*|"
    r"climb\w*|ris(?:e|es|ing)|rall(?:y|ies|ied)|surg\w*|jump\w*|"
    r"gains?|drops?|fall(?:s|ing)?|plunge\w*|tumbl\w*|"
    r"retreat\w*|rebound\w*|recover\w*|navigat\w*|weather\w*|"
    r"tests?|retest\w*|consolidat\w*|"
    r"pulls?\s+back|pullback|"
    r"support|resistance|level|"
    r"downturn|downside|upswing|upside|"
    r"sentiment|volatilit\w*|"
    r"near\s+\$|at\s+\$|around\s+\$|above\s+\$|below\s+\$|to\s+\$|"
    r"could\s+(?:hit|reach|drop|fall|rise|climb|test)|"
    r"may\s+(?:hit|reach|test|drop|fall|rise|dip)|"
    r"eyes?\s+\$|targets?\s+\$|hits?\s+\$|reach\w*\s+\$|"
    r"mixed\s+signals?|market\s+(?:recap|update|wrap)"
    r")\b",
    re.I,
)

# Standalone price-analysis / prediction phrasing — low-value on its own.
_PRICE_ANALYSIS = re.compile(
    r"\bprice\s+(?:prediction|analysis|forecast|target|level|action|outlook|scenarios?)\b"
    r"|\bcan\s+\w+\s+(?:hit|reach|top)\s+\$"
    r"|\b(?:hit|reach|top)\s+\$\d",
    re.I,
)

# Pure market-mood phrasing — flags on its own, no price token needed.
_MARKET_MOOD = re.compile(
    r"\bbroader\s+(?:market|crypto)\b"
    r"|\bmarket\s+(?:pullback|downturn|retreat|swings?|pressure|weakness|sell-?off|rout)\b"
    r"|\bdownward\s+pressure\b"
    r"|\bdownside\s+risk\b"
    r"|\bbear(?:ish)?\s+market\b",
    re.I,
)

# Pure technical-analysis chartist filler — flags on its own. These phrases
# carry no actual news, only price-chart speculation.
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
    """True if the headline is market-noise / price-recap / mood filler."""
    t = (title or "").strip()
    if not t:
        return False
    if _LISTING.search(t):
        return True
    if _PRICE_ANALYSIS.search(t):
        return True
    if _MARKET_MOOD.search(t):
        return True
    if _TA_FILLER.search(t):
        return True
    if (_PRICE.search(t) or _PCT.search(t)) and _MOVE.search(t):
        return True
    return False
