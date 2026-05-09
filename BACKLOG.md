# CuloTon backlog — community features

Pomysły zatwierdzone do realizacji "później". Posortowane od najszybszych do najambitniejszych.
Status: parking lot — nie tknięte, czekają na decyzję kiedy ruszać.

## Średnie (tygodnie pracy)

### 5. Premium $CULO holders feed
Token-gated kanał Telegram — bot weryfikuje wallet (TON Connect / on-chain
balance), trzymający > X $CULO dostaje invite do zamkniętego kanału z
ekskluzywnymi newsami / wcześniejszą publikacją niż public.

Why: daje konkretny utility tokenowi $CULO, którego dziś brakuje (jest tylko
brand). Najlepszy kandydat do podniesienia długoterminowej ceny — gating
tworzy popyt zakupowy i zmniejsza podaż w obrocie.

Zależności: TON Connect SDK, balance check via TON API, separate TG channel,
mechanizm regularnej rewerifikacji (bo holder mógł sprzedać).

### 6. Translation bounty
Community translatorzy zgłaszają poprawki do AI-tłumaczonych artykułów
(open PR na GitHub lub form na stronie), zaakceptowane payout w $CULO.

Why: jakość tłumaczeń RU/PL/DE od AI bywa nierówna — community-edited dla
top artykułów podniesie SEO i zaufanie. Plus: dystrybucja $CULO do
zaangażowanych ludzi, nie do flipperów.

Zależności: review queue, payout flow on-chain, anty-spam.

### 7. Weekly TON podcast (audio)
TTS (np. ElevenLabs) z weekly digestu blog roundup → 5-min mp3 puszczany
na Spotify, Apple Podcasts, X, TG voice message.

Why: nowy kanał dystrybucji, niski koszt (TTS ~$0.30/odcinek), pasuje do
narracji "AI-driven media desk". Audytorium podcastów crypto rośnie.

Zależności: ElevenLabs API, podcast hosting (Anchor/Buzzsprout), RSS feed,
artwork.

### 8. CuloTon Press Kit
Strona `culoton.fun/press` — TON projekty submitują własne newsy do twojego
pipeline'u przez formularz. Po akceptacji wpadają do fetch_news jako źródło,
projekt dostaje powiadomienie + tag.

Why: growth poprzez ich audytorium (zasherują artykuł o sobie do swoich
followersów), pozycjonuje CuloTon jako "the place" dla TON PR-u, dodatkowy
content bez kosztu researchu.

Zależności: form backend (np. Cloudflare Worker → GitHub issues), moderacja,
flow akceptacji.

## Większe / strategiczne (miesiąc+)

### 9. CuloScore — token screener TON
Automatyczny ranking memcoinów / projektów TON: cena, wolumen, holders,
mentions w korpusie CuloTon, social sentiment. Strona `culoton.fun/screener`
aktualizowana 4x/dzień.

Why: ogromny SEO potencjał ("ton meme tokens ranking", "top ton projects"),
realny utility dla traderów, daily-return hook (ludzie wracają codziennie
zobaczyć ranking).

Zależności: GeckoTerminal API per-token, DexScreener, sentiment analysis
nad korpusem newsów, backend storage (SQLite już mamy), UI komponent w Astro.

### 10. NFT "CuloScribe Genesis"
Limitowana kolekcja (np. 500 sztuk) dla pierwszych N holderów / aktywnych
członków TG. Free mint dla tych co spełnią kryterium, secondary market na
Getgems.

Why: status badge dla early supporters, każdy NFT to ambasador (visible w
TON wallet), buduje "in-crowd" dla projektu, secondary royalties → revenue.

Zależności: artist (lub AI art curated), TON NFT contract (collection.fc),
mint UI, kryteria kwalifikacji (snapshot holderów + activity score z bota).

### 11. "Predict TON" mini-game
Daily quiz: bot na TG zadaje pytanie o jutrzejszą cenę TON / wydarzenie,
holderzy stakują $CULO na odpowiedź, wygrywający dzielą pulę.

Why: daily engagement loop, sink dla $CULO (token leci do puli), gamification
trzyma członków w kanale, wirusowy potencjał (screenshoty wygranych).

Zależności: smart contract escrow na TON, oracle dla rozstrzygania, anti-cheat,
KYC-light żeby uniknąć multi-konto farmingu.

---

## Decyzje przy starcie każdego tematu

Dla każdego z powyższych przed implementacją:
1. Konkretny KPI sukcesu (np. "100 holderów w premium feed w 30 dni")
2. Killswitch / koszt anulowania (każda funkcja musi się dać wyłączyć bez breaking site)
3. Kolejność: najpierw te co się **kompounduje z istniejącym pipeline'em** (5, 8, 9 — bazują na newsach które już mamy)
