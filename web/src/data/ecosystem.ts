// Curated map of the TON ecosystem. Verified projects only — anything we can't
// confirm independently (working website, public repo or recognised footprint
// in TON Foundation channels) does NOT belong here. Treat this as the
// editorial layer of the ecosystem map: missing a project is fine, listing a
// fake one is not.
//
// Add entries by category. Keep descriptions to ~120 chars — this page is a
// map, not an encyclopaedia. Detailed coverage belongs in /news.

export interface EcosystemProject {
  name: string;
  url: string;
  description: string;
}

export interface EcosystemCategory {
  id: string;
  title: string;
  blurb: string;
  projects: EcosystemProject[];
}

export const ECOSYSTEM: EcosystemCategory[] = [
  {
    id: 'wallets',
    title: 'Wallets',
    blurb: 'How users hold TON, jettons and NFTs — from in-Telegram custodial flows to fully self-custodial apps.',
    projects: [
      { name: 'Tonkeeper', url: 'https://tonkeeper.com', description: 'The flagship self-custodial TON wallet — mobile, browser ext and TON Connect support.' },
      { name: 'MyTonWallet', url: 'https://mytonwallet.io', description: 'Web and mobile self-custodial wallet with built-in DEX and staking.' },
      { name: 'Tonhub', url: 'https://tonhub.com', description: 'Self-custodial wallet with a focus on jetton swaps and TON Connect.' },
      { name: 'Wallet (in Telegram)', url: 'https://wallet.tg', description: 'Custodial wallet built into the Telegram app — the on-ramp for most TON users.' },
    ],
  },
  {
    id: 'dex',
    title: 'DEXes & DeFi',
    blurb: 'Where jettons get swapped, lent, borrowed and leveraged on TON.',
    projects: [
      { name: 'STON.fi', url: 'https://ston.fi', description: 'The largest DEX on TON by liquidity and volume. AMM-based, jetton-native.' },
      { name: 'DeDust', url: 'https://dedust.io', description: 'The other anchor DEX of TON — multi-pool routing, advanced LP tooling.' },
      { name: 'EVAA Finance', url: 'https://evaa.finance', description: 'Lending and borrowing protocol on TON — supply jettons, borrow against collateral.' },
      { name: 'Storm Trade', url: 'https://storm.tg', description: 'Perpetuals DEX on TON — leverage trading inside a Telegram-native UX.' },
      { name: 'Tonstakers', url: 'https://tonstakers.com', description: 'Liquid staking — get tsTON in exchange for staked TON, use it across DeFi.' },
      { name: 'Bemo', url: 'https://bemo.fi', description: 'Liquid staking on TON with stTON — alternative to Tonstakers.' },
    ],
  },
  {
    id: 'nft',
    title: 'NFTs & Collectibles',
    blurb: 'Marketplaces, collections and the official Telegram-issued asset layer.',
    projects: [
      { name: 'Getgems', url: 'https://getgems.io', description: 'The dominant NFT marketplace on TON — primary mints and secondary trading.' },
      { name: 'Disintar', url: 'https://disintar.io', description: 'NFT marketplace and analytics platform with collection-level data.' },
      { name: 'Fragment', url: 'https://fragment.com', description: "Official Telegram-run platform for usernames and anonymous numbers settled on TON." },
    ],
  },
  {
    id: 'apps',
    title: 'Apps & Mini-Apps',
    blurb: 'Telegram Mini-Apps and consumer products that brought millions of new users to TON.',
    projects: [
      { name: 'Notcoin', url: 'https://notco.in', description: 'The viral tap-to-earn that put TON on every crypto Twitter feed and listed on major CEXes.' },
      { name: 'Catizen', url: 'https://catizen.ai', description: 'TON gaming platform — cat-themed clicker that turned into a hub for mini-app games.' },
      { name: 'Hamster Kombat', url: 'https://hamsterkombatgame.io', description: 'Tap-to-earn that crossed 300M players at peak — one of the largest TON consumer phenomena.' },
    ],
  },
  {
    id: 'infra',
    title: 'Infrastructure & Tooling',
    blurb: 'The validators, explorers and developer toolchains that keep TON running.',
    projects: [
      { name: 'TON Whales', url: 'https://tonwhales.com', description: 'Major TON validator pool — community-run, long-standing operator.' },
      { name: 'TonScan', url: 'https://tonscan.org', description: 'Block explorer for TON — track txs, contracts, jettons and NFTs.' },
      { name: 'TonViewer', url: 'https://tonviewer.com', description: 'TonAPI-backed explorer with a richer transaction graph and contract decoding.' },
      { name: 'TON API', url: 'https://tonapi.io', description: 'Public REST/GraphQL API for TON — the most-used backend for ecosystem dashboards.' },
    ],
  },
  {
    id: 'foundation',
    title: 'Foundation & Official',
    blurb: 'The org-level entities behind the network and the messenger that anchors it.',
    projects: [
      { name: 'TON Foundation', url: 'https://ton.org', description: 'Non-profit stewarding TON protocol development, grants and ecosystem coordination.' },
      { name: 'Telegram', url: 'https://telegram.org', description: 'The messenger app that integrates TON natively for payments, ads and Mini-Apps.' },
      { name: 'TON Society', url: 'https://society.ton.org', description: 'Community and grants arm of the TON Foundation, running ambassador and builder programmes.' },
    ],
  },
];
