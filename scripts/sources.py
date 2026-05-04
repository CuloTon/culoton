"""RSS sources for CuloTon news aggregator.

Each source has:
- name: Display name shown in attribution
- url: Original homepage (for "Read original at..." link)
- feed: RSS feed URL
- keywords: Optional list of keywords/regex patterns to filter entries by.
  Patterns are matched against title + summary as case-insensitive regex.
  Use word boundaries (\\b) to avoid false positives like "Canton" matching "ton".
  If None, all entries are accepted (use only for tag-specific feeds).
"""

# Strict keyword patterns matching TON-specific phrases only.
# Word boundaries prevent matches inside words like "Canton", "Boston", "stone".
TON_KEYWORDS = [
    r"\btoncoin\b",
    r"\bton blockchain\b",
    r"\bton network\b",
    r"\bton ecosystem\b",
    r"\bton foundation\b",
    r"\btelegram open network\b",
    r"\$ton\b",
    r"\bthe open network\b",
]

SOURCES = [
    {
        "name": "Cointelegraph",
        "url": "https://cointelegraph.com",
        "feed": "https://cointelegraph.com/rss/tag/ton",
        "keywords": None,
    },
    {
        "name": "CryptoSlate",
        "url": "https://cryptoslate.com",
        "feed": "https://cryptoslate.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Decrypt",
        "url": "https://decrypt.co",
        "feed": "https://decrypt.co/feed",
        "keywords": TON_KEYWORDS,
    },
    # TON Foundation blog RSS not currently available — ton.org/blog/rss returns HTML.
    # TODO: find alternate official channel (Medium, TONStarter, on-chain governance feed).
]
