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
    r"\btonkeeper\b",
    r"\bjetton\b",
    r"\btact lang\b",
    r"\bton dns\b",
]

SOURCES = [
    # --- Pre-filtered TON-specific feeds (no keyword filter needed) ---
    {
        "name": "Cointelegraph",
        "url": "https://cointelegraph.com",
        "feed": "https://cointelegraph.com/rss/tag/ton",
        "keywords": None,
    },
    {
        "name": "Google News",
        "url": "https://news.google.com",
        "feed": (
            "https://news.google.com/rss/search?"
            "q=%22Toncoin%22+OR+%22TON+blockchain%22+OR+%22TON+Foundation%22"
            "+OR+%22Telegram+Open+Network%22&hl=en-US&gl=US&ceid=US:en"
        ),
        "keywords": None,
    },
    {
        "name": "Reddit r/TheToncoin",
        "url": "https://www.reddit.com/r/TheToncoin/",
        "feed": "https://www.reddit.com/r/TheToncoin/.rss",
        "keywords": None,
    },
    {
        "name": "TON Blockchain (Medium)",
        "url": "https://medium.com/@tonblockchain",
        "feed": "https://medium.com/feed/@tonblockchain",
        "keywords": None,
    },
    {
        "name": "Medium tag: Toncoin",
        "url": "https://medium.com/tag/toncoin",
        "feed": "https://medium.com/feed/tag/toncoin",
        "keywords": None,
    },
    {
        "name": "Medium tag: TON Blockchain",
        "url": "https://medium.com/tag/ton-blockchain",
        "feed": "https://medium.com/feed/tag/ton-blockchain",
        "keywords": None,
    },

    # --- Generic crypto feeds (filter to TON-relevant entries only) ---
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
    {
        "name": "NewsBTC",
        "url": "https://www.newsbtc.com",
        "feed": "https://www.newsbtc.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "AMBCrypto",
        "url": "https://ambcrypto.com",
        "feed": "https://ambcrypto.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "CryptoBriefing",
        "url": "https://cryptobriefing.com",
        "feed": "https://cryptobriefing.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "BeInCrypto",
        "url": "https://beincrypto.com",
        "feed": "https://beincrypto.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "U.Today",
        "url": "https://u.today",
        "feed": "https://u.today/rss",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com",
        "feed": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Crypto.News",
        "url": "https://crypto.news",
        "feed": "https://crypto.news/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "DLNews",
        "url": "https://www.dlnews.com",
        "feed": "https://www.dlnews.com/arc/outboundfeeds/rss/",
        "keywords": TON_KEYWORDS,
    },
]
