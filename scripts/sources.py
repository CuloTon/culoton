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
    r"\bton society\b",
    r"\btelegram open network\b",
    r"\$ton\b",
    r"\bthe open network\b",
    r"\btonkeeper\b",
    r"\btonhub\b",
    r"\bjetton\b",
    r"\btact lang\b",
    r"\bton dns\b",
    r"\btoncenter\b",
    r"\bton space\b",
    r"\bton wallet\b",
    r"\btelegram wallet\b",
    r"\btelegram mini app",
    r"\btelegram mini-app",
    # TON-native protocols, DEXs, marketplaces
    r"\bston\.fi\b",
    r"\bdedust\b",
    r"\bgetgems\b",
    r"\btonstakers\b",
    r"\bevaa protocol\b",
    r"\bstorm trade\b",
    # TON-ecosystem flagship apps / tokens (each unambiguous enough on its own)
    r"\bnotcoin\b",
    r"\bhamster kombat\b",
    r"\bcatizen\b",
    r"\bopen league\b",
    r"\bton accelerator\b",
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
    {
        "name": "Medium tag: Telegram",
        "url": "https://medium.com/tag/telegram",
        "feed": "https://medium.com/feed/tag/telegram",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Reddit r/ton_blockchain",
        "url": "https://www.reddit.com/r/ton_blockchain/",
        "feed": "https://www.reddit.com/r/ton_blockchain/.rss",
        "keywords": None,
    },
    {
        "name": "Bing News: TON",
        "url": "https://www.bing.com/news",
        "feed": (
            "https://www.bing.com/news/search?"
            "q=%22Toncoin%22+OR+%22TON+blockchain%22+OR+%22TON+Foundation%22&format=rss"
        ),
        "keywords": TON_KEYWORDS,
    },

    # --- Generic crypto feeds (filter to TON-relevant entries only) ---
    {
        "name": "Cointelegraph (all)",
        "url": "https://cointelegraph.com",
        "feed": "https://cointelegraph.com/rss",
        "keywords": TON_KEYWORDS,
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
    {
        "name": "The Block",
        "url": "https://www.theblock.co",
        "feed": "https://www.theblock.co/rss.xml",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Blockworks",
        "url": "https://blockworks.co",
        "feed": "https://blockworks.co/feed",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "CoinGape",
        "url": "https://coingape.com",
        "feed": "https://coingape.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Cryptopolitan",
        "url": "https://www.cryptopolitan.com",
        "feed": "https://www.cryptopolitan.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Cryptonews.com",
        "url": "https://cryptonews.com",
        "feed": "https://cryptonews.com/news/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Bitcoin.com News",
        "url": "https://news.bitcoin.com",
        "feed": "https://news.bitcoin.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "ZyCrypto",
        "url": "https://zycrypto.com",
        "feed": "https://zycrypto.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Bitcoinist",
        "url": "https://bitcoinist.com",
        "feed": "https://bitcoinist.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "CoinJournal",
        "url": "https://coinjournal.net",
        "feed": "https://coinjournal.net/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "Invezz Crypto",
        "url": "https://invezz.com",
        "feed": "https://invezz.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "CCN",
        "url": "https://www.ccn.com",
        "feed": "https://www.ccn.com/feed/",
        "keywords": TON_KEYWORDS,
    },
    {
        "name": "The Defiant",
        "url": "https://thedefiant.io",
        "feed": "https://thedefiant.io/api/feed",
        "keywords": TON_KEYWORDS,
    },
]
