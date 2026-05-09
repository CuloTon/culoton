import type { Locale } from '../i18n/strings';

// Curated map of the TON ecosystem. Verified projects only — anything we
// can't confirm independently (working website, public repo or recognised
// footprint in TON Foundation channels) does NOT belong here. Treat this
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
      en: 'How users hold TON, jettons and NFTs — from in-Telegram custodial flows to fully self-custodial apps.',
      ru: 'Как пользователи хранят TON, джеттоны и NFT — от кастодиальных решений внутри Telegram до полностью самокастодиальных приложений.',
      pl: 'Jak użytkownicy trzymają TON, jettony i NFT — od kustodialnych rozwiązań wbudowanych w Telegram po w pełni samokustodialne aplikacje.',
      de: 'Wie Nutzer TON, Jettons und NFTs verwahren — von verwahrenden Lösungen direkt in Telegram bis zu vollständig selbstverwahrenden Apps.',
    },
    projects: [
      {
        name: 'Tonkeeper',
        url: 'https://tonkeeper.com',
        description: {
          en: 'The flagship self-custodial TON wallet — mobile, browser ext and TON Connect support.',
          ru: 'Флагманский самокастодиальный TON-кошелёк — мобильный, расширение для браузера и поддержка TON Connect.',
          pl: 'Flagowy samokustodialny portfel TON — mobilny, rozszerzenie do przeglądarki i wsparcie TON Connect.',
          de: 'Das Flaggschiff-Wallet für TON — mobil, Browser-Erweiterung und TON-Connect-Support, voll selbstverwahrend.',
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
          en: 'Self-custodial wallet with a focus on jetton swaps and TON Connect.',
          ru: 'Самокастодиальный кошелёк с акцентом на свопы джеттонов и TON Connect.',
          pl: 'Samokustodialny portfel ze szczególnym naciskiem na swapy jettonów i TON Connect.',
          de: 'Selbstverwahrendes Wallet mit Fokus auf Jetton-Swaps und TON Connect.',
        },
      },
      {
        name: 'Wallet (in Telegram)',
        url: 'https://wallet.tg',
        description: {
          en: 'Custodial wallet built into the Telegram app — the on-ramp for most TON users.',
          ru: 'Кастодиальный кошелёк, встроенный в Telegram — точка входа для большинства пользователей TON.',
          pl: 'Kustodialny portfel wbudowany w aplikację Telegram — bramka wejściowa dla większości użytkowników TON.',
          de: 'Verwahrendes Wallet direkt in Telegram — der Einstiegspunkt für die meisten TON-Nutzer.',
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
      en: 'Where jettons get swapped, lent, borrowed and leveraged on TON.',
      ru: 'Где джеттоны меняются, выдаются и берутся в долг, торгуются с плечом на TON.',
      pl: 'Gdzie jettony są wymieniane, pożyczane, zaciągane i obracane z dźwignią na TON.',
      de: 'Wo Jettons auf TON getauscht, verliehen, geliehen und gehebelt werden.',
    },
    projects: [
      {
        name: 'STON.fi',
        url: 'https://ston.fi',
        description: {
          en: 'The largest DEX on TON by liquidity and volume. AMM-based, jetton-native.',
          ru: 'Крупнейший DEX на TON по ликвидности и объёму. На основе AMM, нативный для джеттонов.',
          pl: 'Największy DEX na TON pod względem płynności i wolumenu. Oparty na AMM, natywny dla jettonów.',
          de: 'Die größte DEX auf TON nach Liquidität und Volumen. AMM-basiert, jetton-nativ.',
        },
      },
      {
        name: 'DeDust',
        url: 'https://dedust.io',
        description: {
          en: 'The other anchor DEX of TON — multi-pool routing, advanced LP tooling.',
          ru: 'Второй опорный DEX TON — маршрутизация по нескольким пулам, продвинутые инструменты для LP.',
          pl: 'Drugi filar DEX-ów na TON — routing po wielu pulach, zaawansowane narzędzia LP.',
          de: 'Die zweite Anker-DEX von TON — Multi-Pool-Routing, fortgeschrittene LP-Tools.',
        },
      },
      {
        name: 'EVAA Finance',
        url: 'https://evaa.finance',
        description: {
          en: 'Lending and borrowing protocol on TON — supply jettons, borrow against collateral.',
          ru: 'Протокол кредитования на TON — поставляешь джеттоны, берёшь в долг под залог.',
          pl: 'Protokół pożyczek na TON — dostarczasz jettony, bierzesz pod zastaw.',
          de: 'Lending- und Borrowing-Protokoll auf TON — Jettons bereitstellen, gegen Sicherheiten leihen.',
        },
      },
      {
        name: 'Storm Trade',
        url: 'https://storm.tg',
        description: {
          en: 'Perpetuals DEX on TON — leverage trading inside a Telegram-native UX.',
          ru: 'DEX бессрочных контрактов на TON — торговля с плечом в нативном для Telegram интерфейсе.',
          pl: 'DEX kontraktów wieczystych na TON — handel z dźwignią w UX natywnym dla Telegrama.',
          de: 'Perpetuals-DEX auf TON — gehebelter Handel im Telegram-nativen UX.',
        },
      },
      {
        name: 'Tonstakers',
        url: 'https://tonstakers.com',
        description: {
          en: 'Liquid staking — get tsTON in exchange for staked TON, use it across DeFi.',
          ru: 'Ликвидный стейкинг — получаешь tsTON в обмен на застейканный TON, используешь по всему DeFi.',
          pl: 'Płynny staking — dostajesz tsTON w zamian za zastakowane TON, używasz w całym DeFi.',
          de: 'Liquid Staking — tsTON gegen gestaketes TON tauschen und im gesamten DeFi nutzen.',
        },
      },
      {
        name: 'Bemo',
        url: 'https://bemo.fi',
        description: {
          en: 'Liquid staking on TON with stTON — alternative to Tonstakers.',
          ru: 'Ликвидный стейкинг на TON через stTON — альтернатива Tonstakers.',
          pl: 'Płynny staking na TON przez stTON — alternatywa dla Tonstakers.',
          de: 'Liquid Staking auf TON mit stTON — Alternative zu Tonstakers.',
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
          en: 'The dominant NFT marketplace on TON — primary mints and secondary trading.',
          ru: 'Доминирующий NFT-маркетплейс на TON — первичные минты и вторичная торговля.',
          pl: 'Dominujący marketplace NFT na TON — primary minty i obrót wtórny.',
          de: 'Der dominante NFT-Marktplatz auf TON — Primary Mints und Secondary Trading.',
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
          en: 'Official Telegram-run platform for usernames and anonymous numbers settled on TON.',
          ru: 'Официальная платформа Telegram для никнеймов и анонимных номеров, расчёты на TON.',
          pl: 'Oficjalna platforma Telegrama dla nazw użytkownika i anonimowych numerów, rozliczenia na TON.',
          de: 'Offizielle, von Telegram betriebene Plattform für Usernames und anonyme Nummern, abgewickelt auf TON.',
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
      en: 'Telegram Mini-Apps and consumer products that brought millions of new users to TON.',
      ru: 'Telegram Mini Apps и потребительские продукты, которые привели в TON миллионы новых пользователей.',
      pl: 'Telegram Mini-Appy i produkty konsumenckie, które przyciągnęły do TON miliony nowych użytkowników.',
      de: 'Telegram Mini-Apps und Consumer-Produkte, die TON Millionen neuer Nutzer gebracht haben.',
    },
    projects: [
      {
        name: 'Notcoin',
        url: 'https://notcoin.org',
        description: {
          en: 'The viral tap-to-earn that put TON on every crypto Twitter feed and listed on major CEXes.',
          ru: 'Вирусная tap-to-earn-игра, благодаря которой TON попал в ленту каждого крипто-Twitter и на крупные CEX.',
          pl: 'Wirusowa gra tap-to-earn, która wepchnęła TON do każdego feedu crypto Twittera i na duże CEX-y.',
          de: 'Die virale Tap-to-Earn-Sensation, die TON in jeden Krypto-Twitter-Feed brachte und Listings an großen CEXes erhielt.',
        },
      },
      {
        name: 'Catizen',
        url: 'https://catizen.ai',
        description: {
          en: 'TON gaming platform — cat-themed clicker that turned into a hub for mini-app games.',
          ru: 'Игровая платформа на TON — кликер про котов, выросший в хаб для мини-игр.',
          pl: 'Platforma gier na TON — kliker o kotach, który urósł do huba dla mini-gier.',
          de: 'TON-Gaming-Plattform — Katzen-Clicker, der zu einem Hub für Mini-App-Spiele wurde.',
        },
      },
      {
        name: 'Blum',
        url: 'https://blum.io',
        description: {
          en: 'Telegram-native mini-app exchange — swap jettons, claim daily drops, one of the largest active TON retail audiences.',
          ru: 'Биржа в формате Telegram mini-app — свопы джеттонов, ежедневные дропы, одна из крупнейших активных розничных аудиторий TON.',
          pl: 'Giełda w formacie Telegram mini-app — swapy jettonów, dzienne dropy, jedna z największych aktywnych baz retail TON.',
          de: 'Telegram-native Mini-App-Börse — Jetton-Swaps, tägliche Drops, eine der größten aktiven Retail-Audienzen auf TON.',
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
      en: 'The validators, explorers and developer toolchains that keep TON running.',
      ru: 'Валидаторы, эксплореры и инструменты для разработчиков, благодаря которым TON работает.',
      pl: 'Walidatorzy, eksplorery i toolchainy deweloperskie, dzięki którym TON działa.',
      de: 'Die Validatoren, Explorer und Entwickler-Toolchains, die TON am Laufen halten.',
    },
    projects: [
      {
        name: 'TON Whales',
        url: 'https://tonwhales.com',
        description: {
          en: 'Major TON validator pool — community-run, long-standing operator.',
          ru: 'Крупный пул валидаторов TON — управляется сообществом, давно работающий оператор.',
          pl: 'Duży pool walidatorów TON — prowadzony przez społeczność, długoletni operator.',
          de: 'Großer TON-Validator-Pool — community-betrieben, langjähriger Operator.',
        },
      },
      {
        name: 'TonScan',
        url: 'https://tonscan.org',
        description: {
          en: 'Block explorer for TON — track txs, contracts, jettons and NFTs.',
          ru: 'Блок-эксплорер TON — отслеживай транзакции, контракты, джеттоны и NFT.',
          pl: 'Eksplorer bloków TON — śledź transakcje, kontrakty, jettony i NFT.',
          de: 'Block-Explorer für TON — Transaktionen, Verträge, Jettons und NFTs nachverfolgen.',
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
        name: 'TON API',
        url: 'https://tonapi.io',
        description: {
          en: 'Public REST/GraphQL API for TON — the most-used backend for ecosystem dashboards.',
          ru: 'Публичный REST/GraphQL API для TON — самый используемый бэкенд для дашбордов экосистемы.',
          pl: 'Publiczne REST/GraphQL API dla TON — najczęściej używany backend dla dashboardów ekosystemu.',
          de: 'Öffentliche REST/GraphQL-API für TON — das am häufigsten genutzte Backend für Ökosystem-Dashboards.',
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
        name: 'TON Foundation',
        url: 'https://ton.org',
        description: {
          en: 'Non-profit stewarding TON protocol development, grants and ecosystem coordination.',
          ru: 'Некоммерческая организация, ведущая развитие протокола TON, гранты и координацию экосистемы.',
          pl: 'Organizacja non-profit prowadząca rozwój protokołu TON, granty i koordynację ekosystemu.',
          de: 'Gemeinnützige Organisation, die die Entwicklung des TON-Protokolls, Grants und die Ökosystem-Koordination leitet.',
        },
      },
      {
        name: 'Telegram',
        url: 'https://telegram.org',
        description: {
          en: 'The messenger app that integrates TON natively for payments, ads and Mini-Apps.',
          ru: 'Мессенджер, нативно интегрирующий TON для платежей, рекламы и Mini Apps.',
          pl: 'Komunikator, który natywnie integruje TON dla płatności, reklam i Mini-Appów.',
          de: 'Die Messenger-App, die TON nativ für Zahlungen, Werbung und Mini-Apps integriert.',
        },
      },
      {
        name: 'TON Society',
        url: 'https://society.ton.org',
        description: {
          en: 'Community and grants arm of the TON Foundation, running ambassador and builder programmes.',
          ru: 'Комьюнити- и грантовое подразделение TON Foundation, ведёт амбассадорские и билдерские программы.',
          pl: 'Ramię społecznościowo-grantowe TON Foundation, prowadzi programy ambasadorskie i builderskie.',
          de: 'Community- und Grants-Arm der TON Foundation, betreibt Botschafter- und Builder-Programme.',
        },
      },
    ],
  },
];
