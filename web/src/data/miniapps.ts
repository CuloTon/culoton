import type { Locale } from '../i18n/strings';

// Curated map of Telegram Mini Apps in the TON orbit. Strictly for things
// that LIVE inside Telegram (open via t.me/<bot>/<app> or as inline mini
// apps), not regular websites — full-blown wallets, DEX frontends and
// infra belong on /ecosystem, not here.
//
// Each entry must have a verifiable Telegram entry point. If the bot or
// mini app is dead / scammy / impossible to confirm — it does NOT belong
// here. Listing a fake one is far worse than missing a real one.
//
// Description field stays under ~140 chars per locale — this is a hub,
// not a review.

type LocalizedString = Record<Locale, string>;

export interface MiniApp {
  name: string;
  /** Telegram deep link (t.me/<bot> or t.me/<bot>/<app>). Always required. */
  telegramUrl: string;
  /** Optional companion website. */
  webUrl?: string;
  /** Token ticker shipped or claimed by the project, if any. Shown as a chip. */
  token?: string;
  description: LocalizedString;
}

export interface MiniAppCategory {
  id: string;
  title: LocalizedString;
  blurb: LocalizedString;
  apps: MiniApp[];
}

export const MINI_APPS: MiniAppCategory[] = [
  {
    id: 'games',
    title: {
      en: 'Games & clickers',
      ru: 'Игры и кликеры',
      pl: 'Gry i klikery',
      de: 'Spiele & Clicker',
    },
    blurb: {
      en: 'Telegram-native games — from one-tap clickers that minted full-blown tokens to deeper P2E experiences. The category that put TON on the casual-gaming map.',
      ru: 'Игры внутри Telegram — от кликеров одного тапа, выпустивших полноценные токены, до более глубоких P2E-проектов. Именно эта категория вывела TON на массовую игровую сцену.',
      pl: 'Gry w samym Telegramie — od kilkutapowych klikerów, które wypuściły pełnoprawne tokeny, po głębsze projekty P2E. To kategoria, która wprowadziła TON na masową scenę gier.',
      de: 'Spiele direkt in Telegram — vom Ein-Tap-Clicker, der einen vollwertigen Token gestartet hat, bis zu tieferen P2E-Erlebnissen. Diese Kategorie hat TON auf die Casual-Gaming-Karte gesetzt.',
    },
    apps: [
      {
        name: 'Notcoin',
        telegramUrl: 'https://t.me/notcoin_bot',
        webUrl: 'https://notco.in',
        token: 'NOT',
        description: {
          en: 'The clicker that broke TON into the mainstream — 35M+ players tapped a coin, got the $NOT airdrop and stayed for season passes.',
          ru: 'Кликер, который вывел TON в мейнстрим — больше 35 млн игроков тапали монету, получили эирдроп $NOT и остались ради сезонных пропусков.',
          pl: 'Kliker, który wprowadził TON do mainstreamu — ponad 35 mln graczy stukało monetę, dostało airdrop $NOT i zostało przy sezonowych przepustkach.',
          de: 'Der Clicker, der TON in den Mainstream gebracht hat — über 35 Mio. Spieler tippten die Münze, holten den $NOT-Airdrop und blieben für Season-Pässe.',
        },
      },
      {
        name: 'Hamster Kombat',
        telegramUrl: 'https://t.me/hamster_kombat_bot',
        token: 'HMSTR',
        description: {
          en: 'Crypto-exchange-CEO simulator that snowballed past 300M players in 2024 before its $HMSTR launch on TON.',
          ru: 'Симулятор главы криптобиржи, разросшийся в 2024-м до 300+ млн игроков перед запуском $HMSTR на TON.',
          pl: 'Symulator szefa giełdy krypto, który w 2024 urósł do ponad 300 mln graczy przed launchem $HMSTR na TON.',
          de: 'Krypto-Börsen-CEO-Simulator, der 2024 auf über 300 Mio. Spieler anwuchs, bevor $HMSTR auf TON gestartet wurde.',
        },
      },
      {
        name: 'Catizen',
        telegramUrl: 'https://t.me/catizenbot',
        token: 'CATI',
        description: {
          en: 'Idle cat-merge game with serious in-app purchases — among the highest-grossing TON mini apps even before the $CATI listing.',
          ru: 'Айдл-игра про слияние котиков с серьёзными встроенными покупками — одна из самых прибыльных мини-аппок на TON ещё до листинга $CATI.',
          pl: 'Idle z łączeniem kotów i poważnymi zakupami w aplikacji — jedna z najbardziej dochodowych mini-aplikacji na TON jeszcze przed listingiem $CATI.',
          de: 'Idle-Katzen-Merge-Game mit ernsthaften In-App-Käufen — eine der umsatzstärksten TON-Mini-Apps schon vor dem $CATI-Listing.',
        },
      },
      {
        name: 'Blum',
        telegramUrl: 'https://t.me/blum',
        token: 'BLUM',
        description: {
          en: 'Hybrid CEX-mini-app that blends a tap-to-earn drop campaign with an actual order book for memecoins.',
          ru: 'Гибрид мини-приложения и CEX: тап-кампания за дроп параллельно с настоящим стаканом для мемкоинов.',
          pl: 'Hybryda mini-app i CEX-a: kampania tap-to-earn po dropie obok prawdziwej książki zleceń dla memcoinów.',
          de: 'Hybrid aus Mini-App und CEX: Tap-to-Earn-Drop-Kampagne neben einem echten Orderbuch für Memecoins.',
        },
      },
      {
        name: 'PixelTap by Pixelverse',
        telegramUrl: 'https://t.me/pixelversebot',
        token: 'PIXFI',
        description: {
          en: 'Pixel-art PvP brawler with NFT mechs, anchored by the $PIXFI token. Heavier on actual gameplay than most clickers.',
          ru: 'Пиксельный PvP-файтинг с NFT-мехами на токене $PIXFI. Геймплея здесь заметно больше, чем в типичном кликере.',
          pl: 'Pixel-art PvP brawler z NFT-mechami i tokenem $PIXFI. Mechaniki znacznie więcej niż w typowym klikerze.',
          de: 'Pixel-Art-PvP-Brawler mit NFT-Mechs auf Basis von $PIXFI. Deutlich mehr Gameplay als ein klassischer Clicker.',
        },
      },
      {
        name: 'TapSwap',
        telegramUrl: 'https://t.me/tapswap_mirror_1_bot',
        token: 'TAPS',
        description: {
          en: 'One of the original TON clickers — long pre-launch farming season followed by a contested but real $TAPS distribution.',
          ru: 'Один из первых кликеров TON — долгий префарм и спорное, но реальное распределение $TAPS.',
          pl: 'Jeden z pierwszych klikerów TON — długi pre-launch farming i kontrowersyjna, ale realna dystrybucja $TAPS.',
          de: 'Einer der ersten TON-Clicker — lange Pre-Launch-Farm-Saison und eine umstrittene, aber reale $TAPS-Verteilung.',
        },
      },
      {
        name: 'X Empire (Musk Empire)',
        telegramUrl: 'https://t.me/empirebot',
        token: 'X',
        description: {
          en: 'Tycoon-style clicker themed around a certain billionaire — a top-five mini app by DAU through most of 2024.',
          ru: 'Кликер-тайкун, обыгрывающий известного миллиардера — большую часть 2024 держался в топ-5 мини-приложений по DAU.',
          pl: 'Kliker w stylu tycoon z motywem znanego miliardera — przez większość 2024 w top-5 mini-aplikacji po DAU.',
          de: 'Tycoon-Clicker mit dem Thema eines bekannten Milliardärs — den Großteil 2024 in den Top-5-Mini-Apps nach DAU.',
        },
      },
      {
        name: 'MemeFi',
        telegramUrl: 'https://t.me/memefi_coin_bot',
        token: 'MEMEFI',
        description: {
          en: 'Boss-fight clicker where every tap chips at a meme villain — minted $MEMEFI on TON after a long farming season.',
          ru: 'Кликер с боссами, где каждый тап бьёт мемного злодея — выпустил $MEMEFI на TON после длительного фарминга.',
          pl: 'Kliker z bossami, gdzie każdy tap obrywa mem-łotrowi — wypuścił $MEMEFI na TON po długim sezonie farmienia.',
          de: 'Boss-Fight-Clicker, bei dem jeder Tap einem Meme-Bösewicht schadet — startete $MEMEFI auf TON nach langer Farm-Saison.',
        },
      },
    ],
  },
  {
    id: 'earn',
    title: {
      en: 'Earn, drops & quests',
      ru: 'Заработок, дропы и квесты',
      pl: 'Zarobki, dropy i questy',
      de: 'Earn, Drops & Quests',
    },
    blurb: {
      en: 'Mini apps built around quest grinds, social tasks and airdrop campaigns. Less game, more farming — but with real distributions on TON.',
      ru: 'Мини-приложения вокруг квестов, социальных задач и эирдроп-кампаний. Меньше игры, больше фарма — но с реальными раздачами на TON.',
      pl: 'Mini-aplikacje zbudowane wokół questów, zadań społecznościowych i kampanii airdrop. Mniej gry, więcej farmienia — ale z realnymi dystrybucjami na TON.',
      de: 'Mini-Apps rund um Quest-Grinding, Social-Tasks und Airdrop-Kampagnen. Weniger Spiel, mehr Farmen — aber mit echten Verteilungen auf TON.',
    },
    apps: [
      {
        name: 'DOGS',
        telegramUrl: 'https://t.me/dogshouse_bot',
        token: 'DOGS',
        description: {
          en: 'Pavel-Durov-themed dog memecoin distributed by mini-app activity — listed on every major CEX within hours of launch.',
          ru: 'Мемкоин-собака на тему Павла Дурова, раздавался за активность в мини-апе — за часы попал на все крупные CEX.',
          pl: 'Mem-coin pies w temacie Pawła Durowa rozdawany za aktywność w mini-app — w kilka godzin trafił na wszystkie duże CEX-y.',
          de: 'Pavel-Durov-Themen-Hunde-Memecoin, verteilt über Mini-App-Aktivität — innerhalb von Stunden auf jeder großen CEX gelistet.',
        },
      },
      {
        name: 'Major',
        telegramUrl: 'https://t.me/major',
        token: 'MAJOR',
        description: {
          en: 'Squad-recruitment mini app turned mascot token — leaderboard-driven point grind that paid out in $MAJOR on TON.',
          ru: 'Мини-апп про сбор отряда, превратившийся в маскот-токен — гонка по таблице лидеров с выплатой в $MAJOR на TON.',
          pl: 'Mini-app o rekrutacji oddziału zamieniony w token-maskotkę — wyścig po leaderboardzie wypłacany w $MAJOR na TON.',
          de: 'Squad-Rekrutierungs-Mini-App, die zum Maskottchen-Token wurde — Leaderboard-Grind mit Auszahlung in $MAJOR auf TON.',
        },
      },
      {
        name: 'PAWS',
        telegramUrl: 'https://t.me/PAWSOG_bot',
        token: 'PAWS',
        description: {
          en: 'Profile-score and quest hub — auditing Telegram accounts for the ‘paws’ that fed the $PAWS distribution.',
          ru: 'Хаб квестов и оценки профиля — аудит TG-аккаунтов на «лапки», которые легли в основу распределения $PAWS.',
          pl: 'Hub questów i scoringu profilu — audyt kont TG pod kątem „łapek”, które zasiliły dystrybucję $PAWS.',
          de: 'Profil-Score- und Quest-Hub — er prüfte Telegram-Konten auf „Pfoten“, die in die $PAWS-Verteilung einflossen.',
        },
      },
      {
        name: 'Tomarket',
        telegramUrl: 'https://t.me/tomarket_ai_bot',
        token: 'TOMA',
        description: {
          en: 'Quest aggregator with built-in market data — accumulate stars by tapping, trading and inviting, claim $TOMA later.',
          ru: 'Агрегатор квестов со встроенными рыночными данными — копи звёзды через тапы, трейды и инвайты, забирай $TOMA позже.',
          pl: 'Agregator questów z wbudowanymi danymi rynkowymi — gromadź gwiazdki przez tapy, trade i zaproszenia, odbierz $TOMA później.',
          de: 'Quest-Aggregator mit integrierten Marktdaten — sammle Sterne durch Taps, Trades und Einladungen, später $TOMA einlösen.',
        },
      },
      {
        name: 'Yescoin',
        telegramUrl: 'https://t.me/theYescoin_bot',
        token: 'YES',
        description: {
          en: 'Squad-vs-squad clicker that distributed $YES on TON. Mechanics lean closer to a quest grind than to actual gameplay.',
          ru: 'Кликер «отряд против отряда» с раздачей $YES на TON. Механика ближе к фарму квестов, чем к настоящему геймплею.',
          pl: 'Kliker „odział vs odział” z dystrybucją $YES na TON. Mechanika bliżej grindu questów niż realnej rozgrywki.',
          de: 'Squad-vs-Squad-Clicker, der $YES auf TON verteilte. Die Mechanik ähnelt eher Quest-Grinding als echtem Gameplay.',
        },
      },
    ],
  },
  {
    id: 'trading',
    title: {
      en: 'Trading & sniper bots',
      ru: 'Трейдинг и снайпер-боты',
      pl: 'Trading i sniper-boty',
      de: 'Trading- & Sniper-Bots',
    },
    blurb: {
      en: 'On-chain order routers, new-pair scanners and one-tap snipers — the part of the mini-app stack that actually moves real liquidity.',
      ru: 'Маршрутизаторы он-чейн-ордеров, сканеры новых пар и снайперы в один тап — часть мини-аппов, через которую реально движется ликвидность.',
      pl: 'On-chainowe routery zleceń, skanery nowych par i sniper-boty w jeden tap — kawałek stosu mini-app, przez który realnie idzie płynność.',
      de: 'On-Chain-Order-Router, New-Pair-Scanner und Ein-Tap-Sniper — der Teil des Mini-App-Stacks, durch den tatsächlich Liquidität fließt.',
    },
    apps: [
      {
        name: 'STON.fi Sniper',
        telegramUrl: 'https://t.me/stonks_sniper_bot',
        webUrl: 'https://stonksbots.com',
        description: {
          en: 'Flagship sniper from the sTONks stack — sub-100ms execution, custom pre-trade filters, used by 12k+ MAU on the launchpad.',
          ru: 'Флагманский снайпер стека sTONks — исполнение менее 100 мс, настраиваемые фильтры и аудитория 12k+ MAU на лончпаде.',
          pl: 'Flagowy sniper ze stacku sTONks — egzekucja poniżej 100 ms, filtry pre-trade, używany przez 12k+ MAU launchpada.',
          de: 'Flaggschiff-Sniper aus dem sTONks-Stack — Ausführung unter 100 ms, individuelle Pre-Trade-Filter, 12k+ MAU auf dem Launchpad.',
        },
      },
      {
        name: 'Gem Bot',
        telegramUrl: 'https://t.me/gemfinder_bot',
        webUrl: 'https://stonksbots.com',
        description: {
          en: 'Discovery scanner for early jettons — surfaces low-cap pairs against liquidity, holders and contract heuristics.',
          ru: 'Сканер ранних джеттонов — отбирает low-cap пары по ликвидности, держателям и эвристикам контракта.',
          pl: 'Skaner wczesnych jettonów — wyciąga low-cap pary po płynności, holderach i heurystykach kontraktu.',
          de: 'Discovery-Scanner für frühe Jettons — filtert Low-Cap-Paare nach Liquidität, Holdern und Vertragsheuristiken.',
        },
      },
      {
        name: 'New Pairs Bot',
        telegramUrl: 'https://t.me/new_pairs_ton_bot',
        description: {
          en: 'Live alert feed for every new pool on STON.fi and DeDust. Push notifications inside Telegram, no chart-staring required.',
          ru: 'Живая лента алертов про все новые пулы на STON.fi и DeDust. Пуш-уведомления прямо в TG, без зависания над графиком.',
          pl: 'Live feed alertów o każdym nowym poolu na STON.fi i DeDust. Pushe w samym TG, bez wpatrywania się w wykres.',
          de: 'Live-Alert-Feed für jeden neuen Pool auf STON.fi und DeDust. Push-Benachrichtigungen direkt in Telegram, ohne Chart-Starren.',
        },
      },
      {
        name: 'Banana Gun (TON)',
        telegramUrl: 'https://t.me/BananaGunTONbot',
        description: {
          en: 'TON branch of the cross-chain sniper line — copy-trade, anti-rug filters and limit orders from a single chat.',
          ru: 'TON-ветка кроссчейн-линейки снайперов — копитрейд, анти-раг фильтры и лимитные ордера из одного чата.',
          pl: 'TON-owa odnoga cross-chainowej linii sniperów — copy-trade, anty-rug filtry i limit orders z jednego czatu.',
          de: 'TON-Zweig der Cross-Chain-Sniper-Linie — Copy-Trade, Anti-Rug-Filter und Limit-Orders aus einem einzigen Chat.',
        },
      },
      {
        name: 'STON.fi Bot',
        telegramUrl: 'https://t.me/stonfi_bot',
        webUrl: 'https://app.ston.fi',
        description: {
          en: 'In-Telegram order routing for the STON.fi DEX — quote, swap and check positions without leaving the chat.',
          ru: 'Маршрутизация ордеров DEX-а STON.fi прямо в TG — котировки, свопы и проверка позиций без выхода из чата.',
          pl: 'Routing zleceń DEX-a STON.fi w samym TG — kwotowanie, swap i sprawdzanie pozycji bez wychodzenia z czatu.',
          de: 'In-Telegram-Order-Routing für die STON.fi-DEX — Kurs, Swap und Positions-Check, ohne den Chat zu verlassen.',
        },
      },
    ],
  },
  {
    id: 'culture',
    title: {
      en: 'NFTs, social & culture',
      ru: 'NFT, соцсети и культура',
      pl: 'NFT, social i kultura',
      de: 'NFTs, Social & Kultur',
    },
    blurb: {
      en: 'Mini apps that aren’t games and aren’t trading — collectibles, identity and community surfaces native to Telegram.',
      ru: 'Мини-приложения вне игр и трейдинга — коллекционные, идентичность и комьюнити-площадки, родные для Telegram.',
      pl: 'Mini-aplikacje spoza gier i tradingu — kolekcjonerskie, tożsamościowe i społecznościowe powierzchnie natywne dla Telegrama.',
      de: 'Mini-Apps abseits von Spielen und Trading — Sammelobjekte, Identität und Community-Flächen direkt aus Telegram.',
    },
    apps: [
      {
        name: 'Fragment',
        telegramUrl: 'https://t.me/Fragment',
        webUrl: 'https://fragment.com',
        description: {
          en: 'Auction house for Telegram usernames, anonymous numbers and collectible gifts — settles on TON.',
          ru: 'Аукцион имён Telegram, анонимных номеров и коллекционных подарков — расчёты на TON.',
          pl: 'Dom aukcyjny telegramowych nazw, anonimowych numerów i kolekcjonerskich prezentów — rozliczenia w TON.',
          de: 'Auktionshaus für Telegram-Namen, anonyme Nummern und Sammelgeschenke — Abwicklung auf TON.',
        },
      },
      {
        name: 'Getgems',
        telegramUrl: 'https://t.me/getgems',
        webUrl: 'https://getgems.io',
        description: {
          en: 'TON’s biggest NFT marketplace — both as a website and as an in-Telegram mini app for browsing and bidding.',
          ru: 'Крупнейший NFT-маркетплейс TON — и как сайт, и как мини-приложение в Telegram для просмотра и ставок.',
          pl: 'Największy marketplace NFT na TON — zarówno jako strona, jak i mini-app w TG do przeglądania i licytowania.',
          de: 'Der größte NFT-Marktplatz auf TON — als Website und als Mini-App in Telegram zum Stöbern und Bieten.',
        },
      },
      {
        name: 'TON Diamonds',
        telegramUrl: 'https://t.me/tondiamonds_bot',
        webUrl: 'https://ton.diamonds',
        description: {
          en: 'Curated NFT marketplace focused on quality drops, with launchpad mechanics for new TON collections.',
          ru: 'Кураторский NFT-маркетплейс на качественные дропы, с лончпад-механикой для новых коллекций TON.',
          pl: 'Kuratorski marketplace NFT skupiony na jakościowych dropach, z launchpad-mechaniką dla nowych kolekcji TON.',
          de: 'Kuratierter NFT-Marktplatz mit Fokus auf hochwertige Drops und Launchpad-Mechaniken für neue TON-Kollektionen.',
        },
      },
      {
        name: 'TON Society',
        telegramUrl: 'https://t.me/tonsociety',
        webUrl: 'https://society.ton.org',
        description: {
          en: 'Quest and contributor hub run by the TON Foundation — earn ‘Society’ rep for verifiable on-chain and off-chain work.',
          ru: 'Квест-хаб для контрибьюторов от TON Foundation — зарабатывай репутацию «Society» за верифицируемую работу он- и оффчейн.',
          pl: 'Hub questów i kontrybutorów prowadzony przez TON Foundation — zarabiaj rep „Society” za weryfikowalną pracę on- i offchain.',
          de: 'Quest- und Mitwirkenden-Hub der TON Foundation — verdiene „Society“-Reputation für verifizierbare On- und Off-Chain-Arbeit.',
        },
      },
      {
        name: 'Stickerface',
        telegramUrl: 'https://t.me/stickerface_bot',
        description: {
          en: 'Generative-avatar mini app — every Telegram user can mint a sticker pack of themselves, with NFT mode anchored on TON.',
          ru: 'Мини-апп с генеративными аватарами — каждый пользователь TG может выпустить свой стикерпак, с NFT-режимом на TON.',
          pl: 'Mini-app z generatywnymi awatarami — każdy user TG może wybić sticker pack siebie, z trybem NFT zakotwiczonym na TON.',
          de: 'Mini-App für generative Avatare — jeder Telegram-Nutzer kann ein Stickerpaket von sich minten, mit NFT-Modus auf TON.',
        },
      },
    ],
  },
];
