import type { Locale } from '../i18n/strings';

// Curated map of the GRAM ecosystem. Verified projects only — anything we
// can't confirm independently (working website, public repo or recognised
// footprint in GRAM Foundation channels) does NOT belong here. Treat this
// as the editorial layer of the ecosystem map: missing a project is fine,
// listing a fake one is not.
//
// All translatable strings are Record<Locale, string>. Names and URLs stay
// unlocalised. Keep descriptions to ~120 chars in each language — this page
// is a map, not an encyclopaedia.

type LocalizedString = Record<Locale, string>;

export interface EcosystemProject {
  name: string;
  url: string;
  description: LocalizedString;
}

export interface EcosystemCategory {
  id: string;
  title: LocalizedString;
  blurb: LocalizedString;
  projects: EcosystemProject[];
}

export const ECOSYSTEM: EcosystemCategory[] = [
  {
    id: 'wallets',
    title: {
      en: 'Wallets',
      ru: 'Кошельки',
      pl: 'Portfele',
      de: 'Wallets',
    },
    blurb: {
      en: 'How users hold GRAM, jettons and NFTs — from in-Telegram custodial flows to fully self-custodial apps.',
      ru: 'Как пользователи хранят GRAM, джеттоны и NFT — от кастодиальных решений внутри Telegram до полностью самокастодиальных приложений.',
      pl: 'Jak użytkownicy trzymają GRAM, jettony i NFT — od kustodialnych rozwiązań wbudowanych w Telegram po w pełni samokustodialne aplikacje.',
      de: 'Wie Nutzer GRAM, Jettons und NFTs verwahren — von verwahrenden Lösungen direkt in Telegram bis zu vollständig selbstverwahrenden Apps.',
    },
    projects: [
      {
        name: 'Tonkeeper',
        url: 'https://tonkeeper.com',
        description: {
          en: 'The flagship self-custodial GRAM wallet — mobile, browser ext and GRAM Connect support.',
          ru: 'Флагманский самокастодиальный GRAM-кошелёк — мобильный, расширение для браузера и поддержка GRAM Connect.',
          pl: 'Flagowy samokustodialny portfel GRAM — mobilny, rozszerzenie do przeglądarki i wsparcie GRAM Connect.',
          de: 'Das Flaggschiff-Wallet für GRAM — mobil, Browser-Erweiterung und GRAM-Connect-Support, voll selbstverwahrend.',
        },
      },
      {
        name: 'MyTonWallet',
        url: 'https://mytonwallet.io',
        description: {
          en: 'Web and mobile self-custodial wallet with built-in DEX and staking.',
          ru: 'Веб- и мобильный самокастодиальный кошелёк со встроенным DEX и стейкингом.',
          pl: 'Webowy i mobilny samokustodialny portfel z wbudowanym DEX-em i stakingiem.',
          de: 'Selbstverwahrendes Wallet für Web und Mobilgeräte mit integrierter DEX und Staking.',
        },
      },
      {
        name: 'Tonhub',
        url: 'https://tonhub.com',
        description: {
          en: 'Self-custodial wallet with a focus on jetton swaps and GRAM Connect.',
          ru: 'Самокастодиальный кошелёк с акцентом на свопы джеттонов и GRAM Connect.',
          pl: 'Samokustodialny portfel ze szczególnym naciskiem na swapy jettonów i GRAM Connect.',
          de: 'Selbstverwahrendes Wallet mit Fokus auf Jetton-Swaps und GRAM Connect.',
        },
      },
      {
        name: 'Wallet (in Telegram)',
        url: 'https://wallet.tg',
        description: {
          en: 'Custodial wallet built into the Telegram app — the on-ramp for most GRAM users.',
          ru: 'Кастодиальный кошелёк, встроенный в Telegram — точка входа для большинства пользователей GRAM.',
          pl: 'Kustodialny portfel wbudowany w aplikację Telegram — bramka wejściowa dla większości użytkowników GRAM.',
          de: 'Verwahrendes Wallet direkt in Telegram — der Einstiegspunkt für die meisten GRAM-Nutzer.',
        },
      },
    ],
  },
  {
    id: 'dex',
    title: {
      en: 'DEXes & DeFi',
      ru: 'DEX и DeFi',
      pl: 'DEX-y i DeFi',
      de: 'DEXes und DeFi',
    },
    blurb: {
      en: 'Where jettons get swapped, lent, borrowed and leveraged on GRAM.',
      ru: 'Где джеттоны меняются, выдаются и берутся в долг, торгуются с плечом на GRAM.',
      pl: 'Gdzie jettony są wymieniane, pożyczane, zaciągane i obracane z dźwignią na GRAM.',
      de: 'Wo Jettons auf GRAM getauscht, verliehen, geliehen und gehebelt werden.',
    },
    projects: [
      {
        name: 'STON.fi',
        url: 'https://ston.fi',
        description: {
          en: 'The largest DEX on GRAM by liquidity and volume. AMM-based, jetton-native.',
          ru: 'Крупнейший DEX на GRAM по ликвидности и объёму. На основе AMM, нативный для джеттонов.',
          pl: 'Największy DEX na GRAM pod względem płynności i wolumenu. Oparty na AMM, natywny dla jettonów.',
          de: 'Die größte DEX auf GRAM nach Liquidität und Volumen. AMM-basiert, jetton-nativ.',
        },
      },
      {
        name: 'DeDust',
        url: 'https://dedust.io',
        description: {
          en: 'The other anchor DEX of GRAM — multi-pool routing, advanced LP tooling.',
          ru: 'Второй опорный DEX GRAM — маршрутизация по нескольким пулам, продвинутые инструменты для LP.',
          pl: 'Drugi filar DEX-ów na GRAM — routing po wielu pulach, zaawansowane narzędzia LP.',
          de: 'Die zweite Anker-DEX von GRAM — Multi-Pool-Routing, fortgeschrittene LP-Tools.',
        },
      },
      {
        name: 'EVAA Finance',
        url: 'https://evaa.finance',
        description: {
          en: 'Lending and borrowing protocol on GRAM — supply jettons, borrow against collateral.',
          ru: 'Протокол кредитования на GRAM — поставляешь джеттоны, берёшь в долг под залог.',
          pl: 'Protokół pożyczek na GRAM — dostarczasz jettony, bierzesz pod zastaw.',
          de: 'Lending- und Borrowing-Protokoll auf GRAM — Jettons bereitstellen, gegen Sicherheiten leihen.',
        },
      },
      {
        name: 'Storm Trade',
        url: 'https://storm.tg',
        description: {
          en: 'Perpetuals DEX on GRAM — leverage trading inside a Telegram-native UX.',
          ru: 'DEX бессрочных контрактов на GRAM — торговля с плечом в нативном для Telegram интерфейсе.',
          pl: 'DEX kontraktów wieczystych na GRAM — handel z dźwignią w UX natywnym dla Telegrama.',
          de: 'Perpetuals-DEX auf GRAM — gehebelter Handel im Telegram-nativen UX.',
        },
      },
      {
        name: 'Tonstakers',
        url: 'https://tonstakers.com',
        description: {
          en: 'Liquid staking — get tsTON in exchange for staked GRAM, use it across DeFi.',
          ru: 'Ликвидный стейкинг — получаешь tsTON в обмен на застейканный GRAM, используешь по всему DeFi.',
          pl: 'Płynny staking — dostajesz tsTON w zamian za zastakowane GRAM, używasz w całym DeFi.',
          de: 'Liquid Staking — tsTON gegen gestaketes GRAM tauschen und im gesamten DeFi nutzen.',
        },
      },
      {
        name: 'Bemo',
        url: 'https://bemo.fi',
        description: {
          en: 'Liquid staking on GRAM with stTON — alternative to Tonstakers.',
          ru: 'Ликвидный стейкинг на GRAM через stTON — альтернатива Tonstakers.',
          pl: 'Płynny staking na GRAM przez stTON — alternatywa dla Tonstakers.',
          de: 'Liquid Staking auf GRAM mit stTON — Alternative zu Tonstakers.',
        },
      },
    ],
  },
  {
    id: 'nft',
    title: {
      en: 'NFTs & Collectibles',
      ru: 'NFT и коллекции',
      pl: 'NFT i kolekcje',
      de: 'NFTs und Sammlerstücke',
    },
    blurb: {
      en: 'Marketplaces, collections and the official Telegram-issued asset layer.',
      ru: 'Маркетплейсы, коллекции и официальный слой активов от Telegram.',
      pl: 'Marketplace’y, kolekcje i oficjalna warstwa aktywów wydawanych przez Telegram.',
      de: 'Marktplätze, Kollektionen und die offizielle, von Telegram herausgegebene Asset-Schicht.',
    },
    projects: [
      {
        name: 'Getgems',
        url: 'https://getgems.io',
        description: {
          en: 'The dominant NFT marketplace on GRAM — primary mints and secondary trading.',
          ru: 'Доминирующий NFT-маркетплейс на GRAM — первичные минты и вторичная торговля.',
          pl: 'Dominujący marketplace NFT na GRAM — primary minty i obrót wtórny.',
          de: 'Der dominante NFT-Marktplatz auf GRAM — Primary Mints und Secondary Trading.',
        },
      },
      {
        name: 'Disintar',
        url: 'https://disintar.io',
        description: {
          en: 'NFT marketplace and analytics platform with collection-level data.',
          ru: 'NFT-маркетплейс и аналитическая платформа с данными на уровне коллекций.',
          pl: 'Marketplace NFT i platforma analityczna z danymi na poziomie kolekcji.',
          de: 'NFT-Marktplatz und Analyseplattform mit Daten auf Kollektionsebene.',
        },
      },
      {
        name: 'Fragment',
        url: 'https://fragment.com',
        description: {
          en: 'Official Telegram-run platform for usernames and anonymous numbers settled on GRAM.',
          ru: 'Официальная платформа Telegram для никнеймов и анонимных номеров, расчёты на GRAM.',
          pl: 'Oficjalna platforma Telegrama dla nazw użytkownika i anonimowych numerów, rozliczenia na GRAM.',
          de: 'Offizielle, von Telegram betriebene Plattform für Usernames und anonyme Nummern, abgewickelt auf GRAM.',
        },
      },
    ],
  },
  {
    id: 'apps',
    title: {
      en: 'Apps & Mini-Apps',
      ru: 'Приложения и мини-приложения',
      pl: 'Aplikacje i Mini-Appy',
      de: 'Apps und Mini-Apps',
    },
    blurb: {
      en: 'Telegram Mini-Apps and consumer products that brought millions of new users to GRAM.',
      ru: 'Telegram Mini Apps и потребительские продукты, которые привели в GRAM миллионы новых пользователей.',
      pl: 'Telegram Mini-Appy i produkty konsumenckie, które przyciągnęły do GRAM miliony nowych użytkowników.',
      de: 'Telegram Mini-Apps und Consumer-Produkte, die GRAM Millionen neuer Nutzer gebracht haben.',
    },
    projects: [
      {
        name: 'Notcoin',
        url: 'https://notcoin.org',
        description: {
          en: 'The viral tap-to-earn that put GRAM on every crypto Twitter feed and listed on major CEXes.',
          ru: 'Вирусная tap-to-earn-игра, благодаря которой GRAM попал в ленту каждого крипто-Twitter и на крупные CEX.',
          pl: 'Wirusowa gra tap-to-earn, która wepchnęła GRAM do każdego feedu crypto Twittera i na duże CEX-y.',
          de: 'Die virale Tap-to-Earn-Sensation, die GRAM in jeden Krypto-Twitter-Feed brachte und Listings an großen CEXes erhielt.',
        },
      },
      {
        name: 'Catizen',
        url: 'https://catizen.ai',
        description: {
          en: 'GRAM gaming platform — cat-themed clicker that turned into a hub for mini-app games.',
          ru: 'Игровая платформа на GRAM — кликер про котов, выросший в хаб для мини-игр.',
          pl: 'Platforma gier na GRAM — kliker o kotach, który urósł do huba dla mini-gier.',
          de: 'GRAM-Gaming-Plattform — Katzen-Clicker, der zu einem Hub für Mini-App-Spiele wurde.',
        },
      },
      {
        name: 'Blum',
        url: 'https://blum.io',
        description: {
          en: 'Telegram-native mini-app exchange — swap jettons, claim daily drops, one of the largest active GRAM retail audiences.',
          ru: 'Биржа в формате Telegram mini-app — свопы джеттонов, ежедневные дропы, одна из крупнейших активных розничных аудиторий GRAM.',
          pl: 'Giełda w formacie Telegram mini-app — swapy jettonów, dzienne dropy, jedna z największych aktywnych baz retail GRAM.',
          de: 'Telegram-native Mini-App-Börse — Jetton-Swaps, tägliche Drops, eine der größten aktiven Retail-Audienzen auf GRAM.',
        },
      },
      {
        name: 'Maziton (MZT)',
        url: 'https://t.me/MaziTonBot',
        description: {
          en: 'GRAM buybot and trend tracker — live transaction alerts plus the MAZITONTRENDING feed of the hottest jettons right now.',
          ru: 'Buybot и трекер трендов в сети GRAM — живые алерты по транзакциям и лента MAZITONTRENDING с самыми горячими джеттонами прямо сейчас.',
          pl: 'Buybot i tracker trendów w sieci GRAM — alerty o transakcjach na żywo plus feed MAZITONTRENDING z najgorętszymi jettonami właśnie teraz.',
          de: 'GRAM-Buybot und Trend-Tracker — Live-Transaktionsalerts plus der MAZITONTRENDING-Feed mit den aktuell heißesten Jettons.',
        },
      },
    ],
  },
  {
    id: 'infra',
    title: {
      en: 'Infrastructure & Tooling',
      ru: 'Инфраструктура и инструменты',
      pl: 'Infrastruktura i narzędzia',
      de: 'Infrastruktur und Tooling',
    },
    blurb: {
      en: 'The validators, explorers and developer toolchains that keep GRAM running.',
      ru: 'Валидаторы, эксплореры и инструменты для разработчиков, благодаря которым GRAM работает.',
      pl: 'Walidatorzy, eksplorery i toolchainy deweloperskie, dzięki którym GRAM działa.',
      de: 'Die Validatoren, Explorer und Entwickler-Toolchains, die GRAM am Laufen halten.',
    },
    projects: [
      {
        name: 'TON Whales',
        url: 'https://tonwhales.com',
        description: {
          en: 'Major GRAM validator pool — community-run, long-standing operator.',
          ru: 'Крупный пул валидаторов GRAM — управляется сообществом, давно работающий оператор.',
          pl: 'Duży pool walidatorów GRAM — prowadzony przez społeczność, długoletni operator.',
          de: 'Großer GRAM-Validator-Pool — community-betrieben, langjähriger Operator.',
        },
      },
      {
        name: 'TonScan',
        url: 'https://tonscan.org',
        description: {
          en: 'Block explorer for GRAM — track txs, contracts, jettons and NFTs.',
          ru: 'Блок-эксплорер GRAM — отслеживай транзакции, контракты, джеттоны и NFT.',
          pl: 'Eksplorer bloków GRAM — śledź transakcje, kontrakty, jettony i NFT.',
          de: 'Block-Explorer für GRAM — Transaktionen, Verträge, Jettons und NFTs nachverfolgen.',
        },
      },
      {
        name: 'TonViewer',
        url: 'https://tonviewer.com',
        description: {
          en: 'TonAPI-backed explorer with a richer transaction graph and contract decoding.',
          ru: 'Эксплорер на базе TonAPI с расширенным графом транзакций и декодированием контрактов.',
          pl: 'Eksplorer oparty na TonAPI z bogatszym grafem transakcji i dekodowaniem kontraktów.',
          de: 'TonAPI-basierter Explorer mit reichhaltigerem Transaktionsgraphen und Contract-Decoding.',
        },
      },
      {
        name: 'GRAM API',
        url: 'https://tonapi.io',
        description: {
          en: 'Public REST/GraphQL API for GRAM — the most-used backend for ecosystem dashboards.',
          ru: 'Публичный REST/GraphQL API для GRAM — самый используемый бэкенд для дашбордов экосистемы.',
          pl: 'Publiczne REST/GraphQL API dla GRAM — najczęściej używany backend dla dashboardów ekosystemu.',
          de: 'Öffentliche REST/GraphQL-API für GRAM — das am häufigsten genutzte Backend für Ökosystem-Dashboards.',
        },
      },
    ],
  },
  {
    id: 'foundation',
    title: {
      en: 'Foundation & Official',
      ru: 'Foundation и официальные',
      pl: 'Foundation i oficjalne',
      de: 'Foundation und offiziell',
    },
    blurb: {
      en: 'The org-level entities behind the network and the messenger that anchors it.',
      ru: 'Организации, стоящие за сетью, и мессенджер, который её якорит.',
      pl: 'Organizacje stojące za siecią i komunikator, który ją zakotwicza.',
      de: 'Die organisatorischen Entitäten hinter dem Netzwerk und der Messenger, der es verankert.',
    },
    projects: [
      {
        name: 'GRAM Foundation',
        url: 'https://ton.org',
        description: {
          en: 'Non-profit stewarding GRAM protocol development, grants and ecosystem coordination.',
          ru: 'Некоммерческая организация, ведущая развитие протокола GRAM, гранты и координацию экосистемы.',
          pl: 'Organizacja non-profit prowadząca rozwój protokołu GRAM, granty i koordynację ekosystemu.',
          de: 'Gemeinnützige Organisation, die die Entwicklung des GRAM-Protokolls, Grants und die Ökosystem-Koordination leitet.',
        },
      },
      {
        name: 'Telegram',
        url: 'https://telegram.org',
        description: {
          en: 'The messenger app that integrates GRAM natively for payments, ads and Mini-Apps.',
          ru: 'Мессенджер, нативно интегрирующий GRAM для платежей, рекламы и Mini Apps.',
          pl: 'Komunikator, który natywnie integruje GRAM dla płatności, reklam i Mini-Appów.',
          de: 'Die Messenger-App, die GRAM nativ für Zahlungen, Werbung und Mini-Apps integriert.',
        },
      },
      {
        name: 'TON Society',
        url: 'https://society.ton.org',
        description: {
          en: 'Community and grants arm of the GRAM Foundation, running ambassador and builder programmes.',
          ru: 'Комьюнити- и грантовое подразделение GRAM Foundation, ведёт амбассадорские и билдерские программы.',
          pl: 'Ramię społecznościowo-grantowe GRAM Foundation, prowadzi programy ambasadorskie i builderskie.',
          de: 'Community- und Grants-Arm der GRAM Foundation, betreibt Botschafter- und Builder-Programme.',
        },
      },
    ],
  },
];
