"""Shared heuristic: is a news headline low-value "market noise" — i.e.
price-recap filler that should never dominate the channel or the site?

Two scripts use it:
  - fetch_news.py      — skip before spending an API call to rewrite it
  - telegram_notify.py — never pick it as the hourly channel post

We deliberately bias toward *keeping* substantive stories. A headline is only
flagged when it is clearly:
  (a) a price-movement / stability recap — a price token AND a movement verb
      ("TON stabilizes at $2", "TON trades near $1.95"), or
  (b) standalone price-analysis phrasing ("TON price prediction"), or
  (c) the recurring exchange-listing micro-story ("TON/USDT pair on Binance").

A price that merely appears in a substantive headline has no recap verb and
passes — e.g. "Venture firms back Toncoin with $400M as Telegram tops 1B users".
"""

from __future__ import annotations

import re

# A dollar price ($2, $1.95, $400M) or an explicit USD/USDT amount.
_PRICE = re.compile(r"\$\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|usdt|dollars?)\b", re.I)

# Price-movement / stability verbs and phrases that mark a market recap.
_RECAP_VERB = re.compile(
    r"\b("
    r"stabiliz\w*|steady|steadies|hold(?:s|ing)?|hover\w*|"
    r"trad(?:es?|ing)\s+(?:near|at|around|above|below)|"
    r"edges?|dips?|dipped|slips?|slipped|slid\w*|"
    r"climb\w*|ris(?:e|es|ing)|rall(?:y|ies|ied)|surg\w*|jump\w*|"
    r"gains?|drops?|fall(?:s|ing)?|plunge\w*|tumbl\w*|"
    r"pulls?\s+back|pullback|consolidat\w*|retest\w*|"
    r"near\s+\$|at\s+\$|around\s+\$|above\s+\$|below\s+\$|"
    r"could\s+(?:hit|reach|drop|fall|rise|climb)|"
    r"eyes?\s+\$|targets?\s+\$|"
    r"mixed\s+signals?|market\s+(?:recap|update|wrap)"
    r")\b",
    re.I,
)

# Standalone price-analysis phrasing — low-value regardless of a $ token.
_PRICE_ANALYSIS = re.compile(
    r"\bprice\s+(?:prediction|analysis|forecast|target|level|action|outlook)\b",
    re.I,
)

# The recurring "TON/USDT pair on Binance" exchange-listing micro-story.
_LISTING = re.compile(
    r"(?:ton[\s/\-]?usdt|usdt\s+(?:trading\s+)?pair).*"
    r"(?:binance|listed|live|active|spot|trading\s+pair)"
    r"|listed\s+on\s+binance"
    r"|now\s+(?:live|active)\s+on\s+binance"
    r"|trading\s+pair\s+(?:now\s+)?(?:live|active|remains)",
    re.I,
)


def is_low_value_title(title: str) -> bool:
    """True if the headline is market-noise / price-recap filler."""
    t = (title or "").strip()
    if not t:
        return False
    if _LISTING.search(t):
        return True
    if _PRICE_ANALYSIS.search(t):
        return True
    if _PRICE.search(t) and _RECAP_VERB.search(t):
        return True
    return False
