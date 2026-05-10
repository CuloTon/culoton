export type Locale = 'en' | 'ru' | 'pl' | 'de';

export const LOCALES: Locale[] = ['en', 'ru', 'pl', 'de'];

export const LOCALE_LABELS: Record<Locale, string> = {
  en: 'EN',
  ru: 'RU',
  pl: 'PL',
  de: 'DE',
};

export const LOCALE_FULL: Record<Locale, string> = {
  en: 'English',
  ru: 'Русский',
  pl: 'Polski',
  de: 'Deutsch',
};

export const HTML_LANG: Record<Locale, string> = {
  en: 'en',
  ru: 'ru',
  pl: 'pl',
  de: 'de',
};

export const DATE_LOCALE: Record<Locale, string> = {
  en: 'en-US',
  ru: 'ru-RU',
  pl: 'pl-PL',
  de: 'de-DE',
};

interface UIStrings {
  site_title: string;
  site_description: string;
  hero_badge: string;
  hero_headline_html: string;
  hero_blurb: string;
  latest_news: string;
  articles_count: (shown: number, total: number) => string;
  no_news: string;
  nav_news: string;
  nav_blog: string;
  nav_archive: string;
  nav_about: string;
  nav_stonks: string;
  nav_token: string;
  nav_ecosystem: string;
  archive_title: string;
  archive_meta_description: string;
  archive_h: string;
  archive_blurb: string;
  archive_total: (n: number) => string;
  archive_view_all: string;
  archive_no_articles: string;
  stats_h: string;
  stats_online: string;
  stats_total: string;
  stats_avg_hour: string;
  stats_avg_day: string;
  stats_avg_week: string;
  stats_avg_month: string;
  stats_since: (date: string) => string;
  stats_pending: string;
  blog_section_kicker: string;
  blog_section_h: string;
  blog_section_blurb: string;
  blog_section_view_all: string;
  blog_index_title: string;
  blog_index_meta_description: string;
  blog_index_h: string;
  blog_index_blurb: string;
  blog_no_posts: string;
  blog_kind_morning: string;
  blog_kind_noon: string;
  blog_kind_evening: string;
  blog_kind_label: (kind: 'morning' | 'noon' | 'evening') => string;
  blog_articles_covered_label: string;
  blog_byline_lead: string;
  blog_back_to_blog: string;
  footer_tagline_html: string;
  footer_about: string;
  footer_token: string;
  footer_telegram: string;
  footer_x: string;
  footer_pulse: string;
  footer_github: string;
  footer_rss: string;
  footer_edited_by: string;
  source_attribution_lead: string;
  read_original: string;
  back_to_news: string;
  about_title: string;
  about_meta_description: string;
  about_summary: string;
  about_what_we_do_h: string;
  about_what_we_do_p: string;
  about_culoscribe_h: string;
  about_culoscribe_p1: string;
  about_culoscribe_p2: string;
  about_culoscribe_p3: string;
  about_disclaimer_h: string;
  about_disclaimer_p: string;
  about_languages_h: string;
  about_languages_p: string;
  about_contact_p: string;
  date_label: string;
  source_label: string;
  featured_token_pill: string;
  featured_token_h_html: string;
  featured_token_p: string;
  featured_token_btn_info: string;
  featured_token_btn_telegram: string;
  culo_title: string;
  culo_meta_description: string;
  culo_summary: string;
  culo_cta_join: string;
  culo_cta_view: string;
  culo_contract_label: string;
  culo_copy: string;
  culo_copied: string;
  culo_copy_failed: string;
  culo_understanding_h: string;
  culo_understanding_p1_html: string;
  culo_understanding_p2_html: string;
  culo_track_h: string;
  culo_track_li1_html: string;
  culo_track_li2_html: string;
  culo_track_li3_html: string;
  culo_why_h: string;
  culo_why_p: string;
  culo_community_h: string;
  culo_community_p_html: string;
  culo_disclaimer_h: string;
  culo_disclaimer_p: string;
  ecosystem_title: string;
  ecosystem_meta_description: string;
  ecosystem_kicker: string;
  ecosystem_h: string;
  ecosystem_lede: (projects: number, categories: number) => string;
  ecosystem_jump_label: string;
  ecosystem_foot_h: string;
  ecosystem_foot_p_html: string;
  nav_apps: string;
  apps_title: string;
  apps_meta_description: string;
  apps_kicker: string;
  apps_h: string;
  apps_lede: (apps: number, categories: number) => string;
  apps_jump_label: string;
  apps_open_in_telegram: string;
  apps_open_web: string;
  apps_foot_h: string;
  apps_foot_p_html: string;
}

export const UI: Record<Locale, UIStrings> = {
  en: {
    site_title: 'CuloTon — TON Blockchain News',
    site_description: 'Daily news, analysis and updates from the TON blockchain ecosystem. Powered by $CULO.',
    hero_badge: 'TON Ecosystem',
    hero_headline_html: 'News from <span class="ticker">$TON</span> — powered by <span class="ticker">$CULO</span>',
    hero_blurb: 'Independent coverage of the TON blockchain — protocol upgrades, DeFi, payments, Telegram integrations, mini-apps and the broader culture around the network.',
    latest_news: 'Latest News',
    articles_count: (shown, total) => `${shown} of ${total} articles`,
    no_news: 'No news yet.',
    nav_news: 'News',
    nav_blog: 'Blog',
    nav_archive: 'Archive',
    nav_about: 'About',
    nav_stonks: 'sTONks',
    nav_token: '$CULO',
    nav_ecosystem: 'Ecosystem',
    archive_title: 'News archive — CuloTon',
    archive_meta_description: 'Every TON ecosystem story published on CuloTon, grouped by month. The full back-catalogue of independent TON news.',
    archive_h: 'News archive',
    archive_blurb: 'Every story CuloScribe has filed on the TON ecosystem, grouped by month — newest first. Older context for the latest moves.',
    archive_total: (n) => `${n} articles in the archive`,
    archive_view_all: 'Browse the full archive →',
    archive_no_articles: 'The archive is empty for now.',
    stats_h: 'Live desk metrics',
    stats_online: 'Online now',
    stats_total: 'Total visits',
    stats_avg_hour: 'Avg / hour',
    stats_avg_day: 'Avg / day',
    stats_avg_week: 'Avg / week',
    stats_avg_month: 'Avg / month',
    stats_since: (date) => `Tracking since ${date}`,
    stats_pending: 'Numbers will fill in as data is collected.',
    blog_section_kicker: 'CuloTon Blog',
    blog_section_h: 'Daily TON roundups',
    blog_section_blurb: 'Three times a day — morning, noon and evening — CuloScribe takes the latest TON ecosystem news and stitches them into one editorial brief. Catch up in two minutes.',
    blog_section_view_all: 'All roundups →',
    blog_index_title: 'CuloTon Blog — Daily TON roundups',
    blog_index_meta_description: 'Editorial briefs from the TON blockchain ecosystem. Three times a day — morning, noon and evening — CuloScribe synthesises the latest news into one read.',
    blog_index_h: 'CuloTon Blog',
    blog_index_blurb: 'A running editorial diary of the TON ecosystem. Three briefs a day — morning, noon, evening — written by CuloScribe AI on top of the latest reporting.',
    blog_no_posts: 'No roundups yet — the first one will land at the next morning, noon or evening slot.',
    blog_kind_morning: 'Morning roundup',
    blog_kind_noon: 'Noon roundup',
    blog_kind_evening: 'Evening roundup',
    blog_kind_label: (kind) => kind === 'morning' ? 'Morning roundup' : kind === 'noon' ? 'Noon roundup' : 'Evening roundup',
    blog_articles_covered_label: 'Built from these articles',
    blog_byline_lead: 'A CuloScribe AI editorial brief, synthesised from independent TON-ecosystem reporting.',
    blog_back_to_blog: '← Back to blog',
    footer_tagline_html: '<strong>CuloTon</strong> — TON ecosystem news, powered by <span class="footer-ticker">$CULO</span>',
    footer_about: 'About',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
    footer_x: 'X / Twitter',
    footer_pulse: 'sTONks Pulse',
    footer_github: 'GitHub',
    footer_rss: 'RSS',
    footer_edited_by: 'Edited by CuloScribe AI',
    source_attribution_lead: 'This article is based on reporting by',
    read_original: 'Read the original article →',
    back_to_news: '← Back to news',
    about_title: 'About — CuloTon',
    about_meta_description: 'About CuloTon and CuloScribe AI — an independent news platform covering the TON blockchain ecosystem.',
    about_summary: 'CuloTon is an independent news platform covering the TON blockchain ecosystem in four languages. Edited by CuloScribe AI.',
    about_what_we_do_h: 'What we cover',
    about_what_we_do_p: 'We track protocol upgrades, DeFi activity, payments, Telegram integrations, mini-apps, validator news and the broader culture forming around TON. Coverage is sourced from reputable industry publications, official TON Foundation channels and on-chain analytics. Every article is credited and links back to the original source.',
    about_culoscribe_h: 'Meet CuloScribe — our AI editor',
    about_culoscribe_p1: 'CuloScribe is the AI editorial assistant behind every article on this site. Think of CuloScribe as a desk editor: a witty journalist with a serious edge, dry rather than goofy, who reads source material and re-reports it in their own words for our readers.',
    about_culoscribe_p2: 'CuloScribe is <strong>not a translation tool, and not a copy-paste machine</strong>. CuloScribe paraphrases the substance of a source article into an original piece of journalism — its own structure, its own phrasing, its own framing — never reusing the original wording. Facts come from the source. Words come from CuloScribe. Every article on this site links back to the original publication and credits the reporting team that did the underlying work.',
    about_culoscribe_p3: 'For market moves, security incidents, regulatory updates and technical detail, CuloScribe stays strictly serious. For community and culture stories, a little wit is allowed. Never goofy. Never disrespectful to the reporting CuloScribe builds upon.',
    about_disclaimer_h: 'Editorial transparency',
    about_disclaimer_p: 'Articles on CuloTon are written by an AI editor (CuloScribe), based on publicly available reporting from third-party sources. We are not the original reporters. We are an editorial layer that re-tells TON-related news in plain language across four languages, with attribution and a link back to every source. If you are the rights-holder of an original article and have a concern, contact us — we will respond.',
    about_languages_h: 'Available languages',
    about_languages_p: 'CuloTon publishes in English, Russian, Polish and German. Each version is an independent rewrite (not a machine translation), produced by CuloScribe in the same editorial pass.',
    about_contact_p: 'Have a tip, a story we missed, or want to advertise? Reach out via the <a href="https://t.me/culoton">Telegram group</a>.',
    date_label: '📅',
    source_label: '🗞',
    featured_token_pill: 'Featured Token',
    featured_token_h_html: 'The native token of CuloTon — <span class="ticker">$CULO</span>',
    featured_token_p: 'A legacy meme token with a track record across Polygon (10,000X) and SUI — now on TON. Powering this publication and the broader culture around the network.',
    featured_token_btn_info: 'Token info',
    featured_token_btn_telegram: 'Telegram →',
    culo_title: '$CULO — The native token of CuloTon',
    culo_meta_description: '$CULO is a legacy meme token now live on TON. Multi-chain track record: 10,000X on Polygon, success on SUI, now bringing it home on TON.',
    culo_summary: 'A legacy meme token — multi-chain veteran, now live on the TON blockchain.',
    culo_cta_join: 'Join Telegram →',
    culo_cta_view: 'View on Tonviewer',
    culo_contract_label: 'Contract Address (TON)',
    culo_copy: 'Copy',
    culo_copied: 'Copied!',
    culo_copy_failed: 'Copy failed',
    culo_understanding_h: 'Understanding $CULO on TON',
    culo_understanding_p1_html: 'Culo is a legacy meme spanning blockchains since early 2024. The team achieved a phenomenal <strong>10,000X move in MCAP on Polygon</strong>, attracting names like <em>CryptosRUS, JAKE, RODNEY, Crypto Crow, Wendy O</em> and <em>WARREN SAPP</em>, among many others.',
    culo_understanding_p2_html: 'The project also achieved significant success on the <strong>SUI</strong> network, proving its resilience across different ecosystems. We are now committed to following that same path of massive growth on <strong>TON</strong> — including the launch of this dedicated website and a comprehensive development roadmap.',
    culo_track_h: 'Track record',
    culo_track_li1_html: '<strong>2024 — Polygon:</strong> 10,000X market-cap move; coverage and shoutouts from major crypto KOLs',
    culo_track_li2_html: '<strong>SUI:</strong> Strong follow-through on a second chain — proven cross-ecosystem traction',
    culo_track_li3_html: '<strong>2026 — TON:</strong> Launch on the network with native Telegram distribution and the CuloTon news platform',
    culo_why_h: 'Why TON',
    culo_why_p: 'TON — The Open Network, originally conceived by Telegram — is one of the fastest-growing blockchains of 2025-2026. With native Telegram integration, sub-second finality, and a rapidly expanding ecosystem of mini-apps and DeFi protocols, TON is uniquely positioned to bring crypto to hundreds of millions of Telegram users. $CULO arrives on TON with momentum from two prior chains and a community that already knows how to ship.',
    culo_community_h: 'Community',
    culo_community_p_html: 'The fastest way to get involved is the official Telegram group: <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">https://t.me/culoton</a>. News, announcements and trade chatter all happen there.',
    culo_disclaimer_h: 'Disclaimer',
    culo_disclaimer_p: 'Nothing on this page is financial advice. $CULO is a memecoin; cryptocurrencies are highly volatile and you may lose your entire investment. Past performance on Polygon or SUI is no guarantee of future results on TON or any other chain. Always do your own research and only buy what you can afford to lose. CuloTon news coverage is editorially independent of token activity.',
    ecosystem_title: 'TON Ecosystem Map — CuloTon',
    ecosystem_meta_description: 'Curated map of the TON ecosystem — wallets, DEXes, NFT marketplaces, Mini-Apps, infrastructure and the Foundation. Verified projects only.',
    ecosystem_kicker: 'CuloTon Desk · Ecosystem map',
    ecosystem_h: 'The TON ecosystem at a glance',
    ecosystem_lede: (projects, categories) => `A curated map of the projects that move the TON network — what they do, and where to find them. ${projects} projects across ${categories} categories. Editorial selection, not a paid directory.`,
    ecosystem_jump_label: 'Jump to category',
    ecosystem_foot_h: 'Missing or wrong?',
    ecosystem_foot_p_html: 'This map is curated — we only list projects we can independently verify. If your project belongs here, or a listing is outdated, ping the editorial desk on <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegram</a>. No paid placements.',
    nav_apps: 'Mini-Apps',
    apps_title: 'TON Mini-Apps Hub — CuloTon',
    apps_meta_description: 'Curated hub of Telegram Mini Apps in the TON orbit — clickers, P2E games, drop campaigns, sniper bots, NFT marketplaces. Verified Telegram entry points only.',
    apps_kicker: 'CuloTon Desk · Mini-Apps hub',
    apps_h: 'Telegram Mini Apps on TON',
    apps_lede: (apps, categories) => `A hand-picked map of the mini apps that live inside Telegram and settle on TON — games, drops, snipers, NFTs. ${apps} apps across ${categories} categories. Editorial selection, no paid slots.`,
    apps_jump_label: 'Jump to category',
    apps_open_in_telegram: 'Open in Telegram',
    apps_open_web: 'Website',
    apps_foot_h: 'Got an app worth listing?',
    apps_foot_p_html: 'We only add mini apps with a verifiable Telegram entry point and real usage. If your project belongs here — or a listing is outdated — ping the desk on <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegram</a>. No paid placements.',
  },
  ru: {
    site_title: 'CuloTon — Новости блокчейна TON',
    site_description: 'Ежедневные новости, аналитика и обновления экосистемы блокчейна TON. На базе $CULO.',
    hero_badge: 'Экосистема TON',
    hero_headline_html: 'Новости из <span class="ticker">$TON</span> — при поддержке <span class="ticker">$CULO</span>',
    hero_blurb: 'Независимое освещение блокчейна TON — обновления протокола, DeFi, платежи, интеграции с Telegram, мини-приложения и культура вокруг сети.',
    latest_news: 'Свежие новости',
    articles_count: (shown, total) => `${shown} из ${total} статей`,
    no_news: 'Пока нет новостей.',
    nav_news: 'Новости',
    nav_blog: 'Блог',
    nav_archive: 'Архив',
    nav_about: 'О проекте',
    nav_stonks: 'sTONks',
    nav_token: '$CULO',
    nav_ecosystem: 'Экосистема',
    archive_title: 'Архив новостей — CuloTon',
    archive_meta_description: 'Каждая публикация об экосистеме TON на CuloTon, сгруппированная по месяцам. Полный архив независимых новостей TON.',
    archive_h: 'Архив новостей',
    archive_blurb: 'Все материалы CuloScribe об экосистеме TON, сгруппированные по месяцам — новые сверху. Исторический контекст для свежих движений.',
    archive_total: (n) => `всего материалов: ${n}`,
    archive_view_all: 'Перейти в полный архив →',
    archive_no_articles: 'Архив пока пуст.',
    stats_h: 'Метрики деска в реальном времени',
    stats_online: 'Сейчас онлайн',
    stats_total: 'Всего визитов',
    stats_avg_hour: 'Среднее / час',
    stats_avg_day: 'Среднее / день',
    stats_avg_week: 'Среднее / неделя',
    stats_avg_month: 'Среднее / месяц',
    stats_since: (date) => `Учёт с ${date}`,
    stats_pending: 'Цифры появятся по мере накопления данных.',
    blog_section_kicker: 'Блог CuloTon',
    blog_section_h: 'Ежедневные обзоры TON',
    blog_section_blurb: 'Трижды в день — утром, в полдень и вечером — CuloScribe берёт свежие новости экосистемы TON и собирает из них единую редакционную сводку. Полная картина за две минуты.',
    blog_section_view_all: 'Все обзоры →',
    blog_index_title: 'Блог CuloTon — ежедневные обзоры TON',
    blog_index_meta_description: 'Редакционные сводки об экосистеме блокчейна TON. Трижды в день — утром, в полдень и вечером — CuloScribe синтезирует новости в один материал.',
    blog_index_h: 'Блог CuloTon',
    blog_index_blurb: 'Текущий редакционный дневник экосистемы TON. Три сводки в день — утром, в полдень, вечером — написанные CuloScribe AI на основе свежих репортажей.',
    blog_no_posts: 'Пока обзоров нет — первый появится в ближайший утренний, полуденный или вечерний слот.',
    blog_kind_morning: 'Утренний обзор',
    blog_kind_noon: 'Дневной обзор',
    blog_kind_evening: 'Вечерний обзор',
    blog_kind_label: (kind) => kind === 'morning' ? 'Утренний обзор' : kind === 'noon' ? 'Дневной обзор' : 'Вечерний обзор',
    blog_articles_covered_label: 'На основе этих материалов',
    blog_byline_lead: 'Редакционная сводка CuloScribe AI, составленная по независимым репортажам об экосистеме TON.',
    blog_back_to_blog: '← К блогу',
    footer_tagline_html: '<strong>CuloTon</strong> — новости экосистемы TON, на базе <span class="footer-ticker">$CULO</span>',
    footer_about: 'О проекте',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
    footer_x: 'X / Twitter',
    footer_pulse: 'sTONks Pulse',
    footer_github: 'GitHub',
    footer_rss: 'RSS',
    footer_edited_by: 'Редактор: CuloScribe AI',
    source_attribution_lead: 'Статья основана на материалах',
    read_original: 'Читать оригинал →',
    back_to_news: '← К новостям',
    about_title: 'О проекте — CuloTon',
    about_meta_description: 'О CuloTon и CuloScribe AI — независимая платформа новостей экосистемы блокчейна TON.',
    about_summary: 'CuloTon — независимая новостная платформа об экосистеме блокчейна TON на четырёх языках. Редактор — CuloScribe AI.',
    about_what_we_do_h: 'О чём мы пишем',
    about_what_we_do_p: 'Мы следим за обновлениями протокола, активностью DeFi, платежами, интеграциями с Telegram, мини-приложениями, новостями валидаторов и культурой, формирующейся вокруг TON. Источники — авторитетные отраслевые издания, официальные каналы TON Foundation и ончейн-аналитика. Каждая статья содержит ссылку на первоисточник.',
    about_culoscribe_h: 'CuloScribe — наш AI-редактор',
    about_culoscribe_p1: 'CuloScribe — это AI-редактор, который стоит за каждой статьёй на этом сайте. Представьте редактора отдела: ироничного журналиста с серьёзным взглядом, скорее сухого, чем легкомысленного. Он читает первоисточники и пересказывает их своими словами для наших читателей.',
    about_culoscribe_p2: 'CuloScribe — <strong>не переводчик и не машина копипаста</strong>. CuloScribe излагает суть исходной статьи в виде оригинального журналистского материала — собственная структура, собственные формулировки, собственный угол подачи. Никакого повторения формулировок оригинала. Факты — от источника. Слова — от CuloScribe. Каждая статья на сайте содержит ссылку на оригинал и указывает редакцию, проделавшую исходную работу.',
    about_culoscribe_p3: 'Когда речь идёт о движениях рынка, инцидентах безопасности, регуляторных новостях и технических деталях, CuloScribe пишет строго серьёзно. В материалах о сообществе и культуре допускается лёгкая ирония. Никогда — глупо. Никогда — неуважительно к тем, чью работу CuloScribe пересказывает.',
    about_disclaimer_h: 'Редакционная прозрачность',
    about_disclaimer_p: 'Статьи на CuloTon написаны AI-редактором (CuloScribe) на основе публично доступных материалов сторонних источников. Мы не являемся первоначальными авторами репортажей. Мы — редакторский слой, пересказывающий новости TON на четырёх языках простым языком с указанием источника и ссылкой на оригинал. Если вы правообладатель оригинального материала и у вас есть вопрос — свяжитесь с нами, мы ответим.',
    about_languages_h: 'Доступные языки',
    about_languages_p: 'CuloTon выходит на английском, русском, польском и немецком. Каждая версия — самостоятельный пересказ (не машинный перевод), созданный CuloScribe в рамках одной редакторской работы.',
    about_contact_p: 'Есть наводка, новость, которую мы пропустили, или хотите разместить рекламу? Пишите в <a href="https://t.me/culoton">Telegram-группу</a>.',
    date_label: '📅',
    source_label: '🗞',
    featured_token_pill: 'Главный токен',
    featured_token_h_html: 'Нативный токен CuloTon — <span class="ticker">$CULO</span>',
    featured_token_p: 'Легендарный мем-токен с историей на Polygon (10,000X) и SUI — теперь на TON. Питает это издание и культуру вокруг сети.',
    featured_token_btn_info: 'О токене',
    featured_token_btn_telegram: 'Telegram →',
    culo_title: '$CULO — нативный токен CuloTon',
    culo_meta_description: '$CULO — легендарный мем-токен, теперь в сети TON. Кросс-чейн история: 10,000X на Polygon, успех на SUI, теперь на родной TON.',
    culo_summary: 'Легендарный мем-токен — мультичейн-ветеран, теперь в блокчейне TON.',
    culo_cta_join: 'Войти в Telegram →',
    culo_cta_view: 'Смотреть на Tonviewer',
    culo_contract_label: 'Адрес контракта (TON)',
    culo_copy: 'Копировать',
    culo_copied: 'Скопировано!',
    culo_copy_failed: 'Ошибка копирования',
    culo_understanding_h: '$CULO на TON — что это',
    culo_understanding_p1_html: 'Culo — легендарный мем-токен, путешествующий по блокчейнам с начала 2024 года. Команда добилась феноменального <strong>роста капитализации в 10,000 раз на Polygon</strong>, привлекая внимание таких имён, как <em>CryptosRUS, JAKE, RODNEY, Crypto Crow, Wendy O</em> и <em>WARREN SAPP</em>, среди многих других.',
    culo_understanding_p2_html: 'Проект также достиг значительного успеха в сети <strong>SUI</strong>, доказав свою устойчивость в разных экосистемах. Сейчас мы намерены повторить тот же путь масштабного роста на <strong>TON</strong> — включая запуск этого специализированного сайта и развёрнутую дорожную карту развития.',
    culo_track_h: 'История проекта',
    culo_track_li1_html: '<strong>2024 — Polygon:</strong> рост капитализации в 10,000 раз; освещение и упоминания от крупных крипто-KOL',
    culo_track_li2_html: '<strong>SUI:</strong> уверенное продолжение на втором блокчейне — подтверждённая мультиэкосистемная тяга',
    culo_track_li3_html: '<strong>2026 — TON:</strong> запуск в сети с нативной дистрибуцией через Telegram и платформой новостей CuloTon',
    culo_why_h: 'Почему TON',
    culo_why_p: 'TON — The Open Network, изначально задуманный Telegram, — один из самых быстрорастущих блокчейнов 2025-2026. Благодаря нативной интеграции с Telegram, финальности менее секунды и стремительно растущей экосистеме мини-приложений и DeFi-протоколов TON в уникальном положении, чтобы привести крипто к сотням миллионов пользователей Telegram. $CULO приходит на TON с импульсом двух предыдущих блокчейнов и сообществом, которое уже умеет доставлять результат.',
    culo_community_h: 'Сообщество',
    culo_community_p_html: 'Быстрее всего подключиться — через официальную Telegram-группу: <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">https://t.me/culoton</a>. Новости, анонсы и трейдерский чат — всё там.',
    culo_disclaimer_h: 'Дисклеймер',
    culo_disclaimer_p: 'Ничто на этой странице не является финансовой рекомендацией. $CULO — мем-токен; криптовалюты крайне волатильны, и вы можете потерять весь вклад. Прошлые результаты на Polygon или SUI не гарантируют будущих результатов на TON или любом другом блокчейне. Всегда проводите собственное исследование и покупайте только то, что можете позволить себе потерять. Новостное освещение CuloTon редакционно независимо от деятельности токена.',
    ecosystem_title: 'Карта экосистемы TON — CuloTon',
    ecosystem_meta_description: 'Курируемая карта экосистемы TON — кошельки, DEX, NFT-маркетплейсы, Mini Apps, инфраструктура и Foundation. Только проверенные проекты.',
    ecosystem_kicker: 'CuloTon Desk · Карта экосистемы',
    ecosystem_h: 'Экосистема TON одним взглядом',
    ecosystem_lede: (projects, categories) => `Курируемая карта проектов, которые двигают сеть TON — что они делают и где их найти. ${projects} проектов в ${categories} категориях. Редакционный выбор, не платный каталог.`,
    ecosystem_jump_label: 'Перейти к категории',
    ecosystem_foot_h: 'Не нашли проект или нужна правка?',
    ecosystem_foot_p_html: 'Это курируемая карта — мы перечисляем только проекты, которые можем независимо подтвердить. Если ваш проект должен быть здесь или запись устарела — напишите редакции в <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegram</a>. Платных размещений нет.',
    nav_apps: 'Mini-Apps',
    apps_title: 'TON Mini-Apps Hub — CuloTon',
    apps_meta_description: 'Курируемый хаб Telegram Mini Apps в орбите TON — кликеры, P2E-игры, дроп-кампании, снайпер-боты, NFT-маркетплейсы. Только подтверждённые точки входа в Telegram.',
    apps_kicker: 'CuloTon Desk · Хаб мини-приложений',
    apps_h: 'Telegram Mini Apps на TON',
    apps_lede: (apps, categories) => `Подобранная карта мини-приложений, которые живут внутри Telegram и расчёт ведут на TON — игры, дропы, снайперы, NFT. ${apps} приложений в ${categories} категориях. Редакционный выбор, без платных мест.`,
    apps_jump_label: 'Перейти к категории',
    apps_open_in_telegram: 'Открыть в Telegram',
    apps_open_web: 'Сайт',
    apps_foot_h: 'Есть приложение, которое стоит добавить?',
    apps_foot_p_html: 'Мы добавляем только мини-приложения с подтверждаемой точкой входа в Telegram и реальной аудиторией. Если ваш проект должен быть здесь — или запись устарела — напишите редакции в <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegram</a>. Платных размещений нет.',
  },
  pl: {
    site_title: 'CuloTon — Wiadomości z blockchaina TON',
    site_description: 'Codzienne wiadomości, analizy i aktualizacje z ekosystemu blockchaina TON. Napędzane przez $CULO.',
    hero_badge: 'Ekosystem TON',
    hero_headline_html: 'Wiadomości z <span class="ticker">$TON</span> — napędzane przez <span class="ticker">$CULO</span>',
    hero_blurb: 'Niezależne pokrycie blockchaina TON — aktualizacje protokołu, DeFi, płatności, integracje z Telegramem, mini-aplikacje i kultura wokół sieci.',
    latest_news: 'Najnowsze wiadomości',
    articles_count: (shown, total) => `${shown} z ${total} artykułów`,
    no_news: 'Brak wiadomości.',
    nav_news: 'Wiadomości',
    nav_blog: 'Blog',
    nav_archive: 'Archiwum',
    nav_about: 'O nas',
    nav_stonks: 'sTONks',
    nav_token: '$CULO',
    nav_ecosystem: 'Ekosystem',
    archive_title: 'Archiwum wiadomości — CuloTon',
    archive_meta_description: 'Każda historia z ekosystemu TON opublikowana na CuloTon, pogrupowana po miesiącach. Pełne archiwum niezależnych newsów TON.',
    archive_h: 'Archiwum wiadomości',
    archive_blurb: 'Wszystkie materiały CuloScribe o ekosystemie TON, pogrupowane po miesiącach — najnowsze na górze. Kontekst historyczny dla świeżych ruchów.',
    archive_total: (n) => `materiałów łącznie: ${n}`,
    archive_view_all: 'Przejdź do pełnego archiwum →',
    archive_no_articles: 'Archiwum jest na razie puste.',
    stats_h: 'Metryki redakcji na żywo',
    stats_online: 'Teraz online',
    stats_total: 'Łącznie wizyt',
    stats_avg_hour: 'Śr. / godz.',
    stats_avg_day: 'Śr. / dzień',
    stats_avg_week: 'Śr. / tydzień',
    stats_avg_month: 'Śr. / mies.',
    stats_since: (date) => `Liczone od ${date}`,
    stats_pending: 'Cyfry wypełnią się w miarę zbierania danych.',
    blog_section_kicker: 'Blog CuloTon',
    blog_section_h: 'Codzienne podsumowania TON',
    blog_section_blurb: 'Trzy razy dziennie — rano, w południe i wieczorem — CuloScribe bierze świeże newsy z ekosystemu TON i składa je w jedną redakcyjną notatkę. Pełen obraz w dwie minuty.',
    blog_section_view_all: 'Wszystkie podsumowania →',
    blog_index_title: 'Blog CuloTon — codzienne podsumowania TON',
    blog_index_meta_description: 'Redakcyjne podsumowania ekosystemu blockchaina TON. Trzy razy dziennie — rano, w południe i wieczorem — CuloScribe syntetyzuje newsy w jeden materiał.',
    blog_index_h: 'Blog CuloTon',
    blog_index_blurb: 'Bieżący redakcyjny dziennik ekosystemu TON. Trzy notatki dziennie — rano, w południe, wieczorem — pisane przez CuloScribe AI na bazie świeżych doniesień.',
    blog_no_posts: 'Brak podsumowań — pierwsze pojawi się w najbliższym slocie porannym, południowym lub wieczornym.',
    blog_kind_morning: 'Podsumowanie poranne',
    blog_kind_noon: 'Podsumowanie południowe',
    blog_kind_evening: 'Podsumowanie wieczorne',
    blog_kind_label: (kind) => kind === 'morning' ? 'Podsumowanie poranne' : kind === 'noon' ? 'Podsumowanie południowe' : 'Podsumowanie wieczorne',
    blog_articles_covered_label: 'Na bazie tych artykułów',
    blog_byline_lead: 'Redakcyjne podsumowanie CuloScribe AI, zsyntetyzowane z niezależnych doniesień o ekosystemie TON.',
    blog_back_to_blog: '← Wróć do bloga',
    footer_tagline_html: '<strong>CuloTon</strong> — wiadomości z ekosystemu TON, napędzane przez <span class="footer-ticker">$CULO</span>',
    footer_about: 'O nas',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
    footer_x: 'X / Twitter',
    footer_pulse: 'sTONks Pulse',
    footer_github: 'GitHub',
    footer_rss: 'RSS',
    footer_edited_by: 'Redaktor: CuloScribe AI',
    source_attribution_lead: 'Artykuł powstał w oparciu o materiał',
    read_original: 'Przeczytaj oryginał →',
    back_to_news: '← Powrót do wiadomości',
    about_title: 'O nas — CuloTon',
    about_meta_description: 'O CuloTon i CuloScribe AI — niezależnej platformie wiadomości o ekosystemie blockchaina TON.',
    about_summary: 'CuloTon to niezależna platforma wiadomości o ekosystemie blockchaina TON, dostępna w czterech językach. Redagowana przez CuloScribe AI.',
    about_what_we_do_h: 'Co opisujemy',
    about_what_we_do_p: 'Śledzimy aktualizacje protokołu, aktywność DeFi, płatności, integracje z Telegramem, mini-aplikacje, wiadomości od walidatorów oraz kulturę narastającą wokół TON. Źródła to renomowane publikacje branżowe, oficjalne kanały TON Foundation i analityka on-chain. Każdy artykuł zawiera link do oryginału.',
    about_culoscribe_h: 'CuloScribe — nasz redaktor AI',
    about_culoscribe_p1: 'CuloScribe to redaktor AI, który stoi za każdym artykułem na tej stronie. Pomyśl o nim jak o redaktorze prowadzącym: dowcipnym dziennikarzu z poważnym podejściem, raczej sucho ironicznym niż błaznującym. Czyta materiały źródłowe i opowiada je własnymi słowami dla naszych czytelników.',
    about_culoscribe_p2: 'CuloScribe to <strong>nie tłumacz i nie maszyna do kopiowania</strong>. CuloScribe parafrazuje treść artykułu źródłowego, tworząc oryginalny materiał dziennikarski — własna struktura, własne sformułowania, własna rama narracyjna. Nigdy nie powiela oryginalnych zwrotów. Fakty pochodzą ze źródła. Słowa pochodzą od CuloScribe. Każdy artykuł na tej stronie linkuje do oryginalnej publikacji i wskazuje redakcję, która wykonała pracę u podstaw.',
    about_culoscribe_p3: 'W sprawach rynku, incydentów bezpieczeństwa, regulacji i szczegółów technicznych CuloScribe pisze ściśle poważnie. W materiałach o społeczności i kulturze pozwala sobie na odrobinę ironii. Nigdy głupio. Nigdy bez szacunku dla pracy, na której bazuje.',
    about_disclaimer_h: 'Przejrzystość redakcyjna',
    about_disclaimer_p: 'Artykuły na CuloTon pisze redaktor AI (CuloScribe) na podstawie publicznie dostępnych materiałów stron trzecich. Nie jesteśmy oryginalnymi reporterami. Jesteśmy warstwą redakcyjną, która opowiada wiadomości o TON prostym językiem w czterech wersjach językowych — z atrybucją i linkiem do każdego źródła. Jeśli jesteś właścicielem praw do oryginalnego materiału i masz zastrzeżenia, skontaktuj się z nami — odpowiemy.',
    about_languages_h: 'Dostępne języki',
    about_languages_p: 'CuloTon ukazuje się po angielsku, rosyjsku, polsku i niemiecku. Każda wersja to niezależne opracowanie (nie tłumaczenie maszynowe), wykonane przez CuloScribe w jednym przejściu redakcyjnym.',
    about_contact_p: 'Masz cynk, wiadomość, którą przegapiliśmy, albo chcesz się reklamować? Pisz na <a href="https://t.me/culoton">grupę Telegram</a>.',
    date_label: '📅',
    source_label: '🗞',
    featured_token_pill: 'Główny token',
    featured_token_h_html: 'Natywny token CuloTon — <span class="ticker">$CULO</span>',
    featured_token_p: 'Legendarny memecoin z historią na Polygon (10,000X) i SUI — teraz na TON. Zasila to wydawnictwo i kulturę wokół sieci.',
    featured_token_btn_info: 'O tokenie',
    featured_token_btn_telegram: 'Telegram →',
    culo_title: '$CULO — natywny token CuloTon',
    culo_meta_description: '$CULO to legendarny memecoin, teraz dostępny w sieci TON. Cross-chain track record: 10,000X na Polygonie, sukces na SUI, teraz na rodzimym TON.',
    culo_summary: 'Legendarny memecoin — weteran wielu blockchainów, teraz w sieci TON.',
    culo_cta_join: 'Dołącz na Telegramie →',
    culo_cta_view: 'Zobacz na Tonviewer',
    culo_contract_label: 'Adres kontraktu (TON)',
    culo_copy: 'Kopiuj',
    culo_copied: 'Skopiowano!',
    culo_copy_failed: 'Błąd kopiowania',
    culo_understanding_h: '$CULO na TON — o co chodzi',
    culo_understanding_p1_html: 'Culo to legendarny mem przemierzający blockchainy od początku 2024 roku. Zespół osiągnął fenomenalny <strong>wzrost kapitalizacji 10,000X na Polygonie</strong>, przyciągając takie nazwiska jak <em>CryptosRUS, JAKE, RODNEY, Crypto Crow, Wendy O</em> oraz <em>WARREN SAPP</em>, wśród wielu innych.',
    culo_understanding_p2_html: 'Projekt odniósł także znaczący sukces w sieci <strong>SUI</strong>, dowodząc odporności w różnych ekosystemach. Obecnie kontynuujemy tę samą ścieżkę masowego wzrostu na <strong>TON</strong> — w tym uruchomienie tej dedykowanej strony oraz rozbudowaną mapę drogową rozwoju.',
    culo_track_h: 'Historia projektu',
    culo_track_li1_html: '<strong>2024 — Polygon:</strong> wzrost kapitalizacji 10,000X; pokrycie i wzmianki od czołowych krypto-KOL-ów',
    culo_track_li2_html: '<strong>SUI:</strong> mocna kontynuacja na drugim blockchainie — potwierdzona przyczepność między ekosystemami',
    culo_track_li3_html: '<strong>2026 — TON:</strong> debiut w sieci z natywną dystrybucją przez Telegram oraz platformą wiadomości CuloTon',
    culo_why_h: 'Dlaczego TON',
    culo_why_p: 'TON — The Open Network, pierwotnie zaprojektowany przez Telegram — to jeden z najszybciej rosnących blockchainów lat 2025-2026. Dzięki natywnej integracji z Telegramem, finalności poniżej sekundy oraz dynamicznie rosnącemu ekosystemowi mini-aplikacji i protokołów DeFi, TON ma unikalną pozycję, by dostarczyć kryptowaluty setkom milionów użytkowników Telegrama. $CULO wchodzi na TON z impetem z dwóch wcześniejszych blockchainów i społecznością, która już potrafi dowieźć wynik.',
    culo_community_h: 'Społeczność',
    culo_community_p_html: 'Najszybszy sposób, by się włączyć, to oficjalna grupa Telegram: <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">https://t.me/culoton</a>. Wiadomości, ogłoszenia i rozmowy traderów — wszystko tam.',
    culo_disclaimer_h: 'Zastrzeżenie',
    culo_disclaimer_p: 'Nic na tej stronie nie stanowi porady finansowej. $CULO to memecoin; kryptowaluty są wysoce zmienne i możesz stracić całą inwestycję. Wyniki z przeszłości na Polygonie lub SUI nie gwarantują przyszłych rezultatów na TON ani na żadnym innym blockchainie. Zawsze rób własny research i kupuj wyłącznie tyle, ile możesz stracić. Newsy na CuloTon są redakcyjnie niezależne od aktywności tokena.',
    ecosystem_title: 'Mapa ekosystemu TON — CuloTon',
    ecosystem_meta_description: 'Curated mapa ekosystemu TON — portfele, DEX-y, marketplace’y NFT, Mini-Appy, infrastruktura i Foundation. Tylko zweryfikowane projekty.',
    ecosystem_kicker: 'CuloTon Desk · Mapa ekosystemu',
    ecosystem_h: 'Ekosystem TON na jeden rzut oka',
    ecosystem_lede: (projects, categories) => `Curated mapa projektów, które realnie napędzają sieć TON — co robią i gdzie ich znaleźć. ${projects} projektów w ${categories} kategoriach. Selekcja redakcyjna, nie płatny katalog.`,
    ecosystem_jump_label: 'Przejdź do kategorii',
    ecosystem_foot_h: 'Brakuje czegoś albo coś nie tak?',
    ecosystem_foot_p_html: 'Ta mapa jest curated — wymieniamy tylko projekty, które potrafimy niezależnie zweryfikować. Jeśli twój projekt powinien tu być albo wpis jest nieaktualny — pisz do redakcji na <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegramie</a>. Bez płatnych umieszczeń.',
    nav_apps: 'Mini-Appy',
    apps_title: 'TON Mini-Apps Hub — CuloTon',
    apps_meta_description: 'Curated hub Telegram Mini Apps w orbicie TON — klikery, gry P2E, kampanie dropowe, sniper-boty, marketplace’y NFT. Tylko zweryfikowane wejścia w Telegramie.',
    apps_kicker: 'CuloTon Desk · Hub mini-aplikacji',
    apps_h: 'Telegram Mini Apps na TON',
    apps_lede: (apps, categories) => `Ręcznie dobrana mapa mini-aplikacji, które żyją w samym Telegramie, a rozliczają się na TON — gry, dropy, snipery, NFT. ${apps} aplikacji w ${categories} kategoriach. Selekcja redakcyjna, bez płatnych miejsc.`,
    apps_jump_label: 'Przejdź do kategorii',
    apps_open_in_telegram: 'Otwórz w Telegramie',
    apps_open_web: 'Strona',
    apps_foot_h: 'Masz appkę, która powinna tu być?',
    apps_foot_p_html: 'Dorzucamy tylko mini-aplikacje z weryfikowalnym wejściem w Telegramie i realną aktywnością. Jeśli twój projekt powinien tu być — albo wpis jest nieaktualny — napisz do redakcji na <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegramie</a>. Bez płatnych umieszczeń.',
  },
  de: {
    site_title: 'CuloTon — Nachrichten zur TON-Blockchain',
    site_description: 'Tägliche Nachrichten, Analysen und Updates aus dem TON-Blockchain-Ökosystem. Powered by $CULO.',
    hero_badge: 'TON-Ökosystem',
    hero_headline_html: 'Nachrichten aus <span class="ticker">$TON</span> — powered by <span class="ticker">$CULO</span>',
    hero_blurb: 'Unabhängige Berichterstattung über die TON-Blockchain — Protokoll-Upgrades, DeFi, Payments, Telegram-Integrationen, Mini-Apps und die Kultur rund um das Netzwerk.',
    latest_news: 'Aktuelle Nachrichten',
    articles_count: (shown, total) => `${shown} von ${total} Artikeln`,
    no_news: 'Noch keine Nachrichten.',
    nav_news: 'Nachrichten',
    nav_blog: 'Blog',
    nav_archive: 'Archiv',
    nav_about: 'Über uns',
    nav_stonks: 'sTONks',
    nav_token: '$CULO',
    nav_ecosystem: 'Ökosystem',
    archive_title: 'Nachrichtenarchiv — CuloTon',
    archive_meta_description: 'Jede Geschichte aus dem TON-Ökosystem, die auf CuloTon veröffentlicht wurde, nach Monaten gruppiert. Das vollständige Archiv unabhängiger TON-Nachrichten.',
    archive_h: 'Nachrichtenarchiv',
    archive_blurb: 'Alle Beiträge, die CuloScribe zum TON-Ökosystem verfasst hat — nach Monaten gruppiert, neueste zuerst. Historischer Kontext für die jüngsten Bewegungen.',
    archive_total: (n) => `Beiträge im Archiv: ${n}`,
    archive_view_all: 'Zum vollständigen Archiv →',
    archive_no_articles: 'Das Archiv ist derzeit leer.',
    stats_h: 'Live-Desk-Metriken',
    stats_online: 'Jetzt online',
    stats_total: 'Besuche gesamt',
    stats_avg_hour: 'Ø / Stunde',
    stats_avg_day: 'Ø / Tag',
    stats_avg_week: 'Ø / Woche',
    stats_avg_month: 'Ø / Monat',
    stats_since: (date) => `Erfassung seit ${date}`,
    stats_pending: 'Die Zahlen füllen sich, sobald Daten vorliegen.',
    blog_section_kicker: 'CuloTon Blog',
    blog_section_h: 'Tägliche TON-Roundups',
    blog_section_blurb: 'Dreimal täglich — morgens, mittags und abends — verdichtet CuloScribe die aktuellen News aus dem TON-Ökosystem zu einem redaktionellen Briefing. In zwei Minuten auf dem Stand.',
    blog_section_view_all: 'Alle Roundups →',
    blog_index_title: 'CuloTon Blog — tägliche TON-Roundups',
    blog_index_meta_description: 'Redaktionelle Briefings aus dem TON-Blockchain-Ökosystem. Dreimal täglich — morgens, mittags und abends — synthetisiert CuloScribe die aktuelle Berichterstattung zu einem Stück.',
    blog_index_h: 'CuloTon Blog',
    blog_index_blurb: 'Ein laufendes redaktionelles Tagebuch des TON-Ökosystems. Drei Briefings pro Tag — morgens, mittags, abends — verfasst von CuloScribe AI auf Basis aktueller Berichterstattung.',
    blog_no_posts: 'Noch keine Roundups — das erste landet im nächsten Morgen-, Mittags- oder Abend-Slot.',
    blog_kind_morning: 'Morgen-Roundup',
    blog_kind_noon: 'Mittags-Roundup',
    blog_kind_evening: 'Abend-Roundup',
    blog_kind_label: (kind) => kind === 'morning' ? 'Morgen-Roundup' : kind === 'noon' ? 'Mittags-Roundup' : 'Abend-Roundup',
    blog_articles_covered_label: 'Auf Basis dieser Artikel',
    blog_byline_lead: 'Ein redaktionelles Briefing von CuloScribe AI, synthetisiert aus unabhängiger Berichterstattung zum TON-Ökosystem.',
    blog_back_to_blog: '← Zurück zum Blog',
    footer_tagline_html: '<strong>CuloTon</strong> — Nachrichten aus dem TON-Ökosystem, powered by <span class="footer-ticker">$CULO</span>',
    footer_about: 'Über uns',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
    footer_x: 'X / Twitter',
    footer_pulse: 'sTONks Pulse',
    footer_github: 'GitHub',
    footer_rss: 'RSS',
    footer_edited_by: 'Redaktion: CuloScribe AI',
    source_attribution_lead: 'Dieser Artikel basiert auf Berichterstattung von',
    read_original: 'Originalartikel lesen →',
    back_to_news: '← Zurück zu den Nachrichten',
    about_title: 'Über uns — CuloTon',
    about_meta_description: 'Über CuloTon und CuloScribe AI — eine unabhängige Nachrichtenplattform zum TON-Blockchain-Ökosystem.',
    about_summary: 'CuloTon ist eine unabhängige Nachrichtenplattform zum TON-Blockchain-Ökosystem, verfügbar in vier Sprachen. Redaktion: CuloScribe AI.',
    about_what_we_do_h: 'Worüber wir berichten',
    about_what_we_do_p: 'Wir verfolgen Protokoll-Upgrades, DeFi-Aktivitäten, Payments, Telegram-Integrationen, Mini-Apps, Validator-Nachrichten und die Kultur, die sich rund um TON entwickelt. Quellen sind renommierte Branchenpublikationen, offizielle Kanäle der TON Foundation und On-Chain-Analytik. Jeder Artikel enthält einen Link zur Originalquelle.',
    about_culoscribe_h: 'CuloScribe — unsere KI-Redaktion',
    about_culoscribe_p1: 'CuloScribe ist die KI-Redaktion hinter jedem Artikel auf dieser Seite. Stellen Sie sich CuloScribe als Desk-Editor vor: ein geistreicher Journalist mit ernster Schlagseite, eher trocken als albern. CuloScribe liest Quellmaterial und erzählt es mit eigenen Worten für unsere Leser nach.',
    about_culoscribe_p2: 'CuloScribe ist <strong>kein Übersetzungstool und keine Copy-Paste-Maschine</strong>. CuloScribe paraphrasiert die Substanz eines Quellartikels in einen eigenständigen journalistischen Text — eigene Struktur, eigene Formulierungen, eigene Einordnung. Originalformulierungen werden nie übernommen. Fakten kommen aus der Quelle. Worte kommen von CuloScribe. Jeder Artikel auf dieser Seite verlinkt zur Originalpublikation und nennt die Redaktion, die die zugrundeliegende Arbeit geleistet hat.',
    about_culoscribe_p3: 'Bei Marktbewegungen, Sicherheitsvorfällen, regulatorischen Themen und technischen Details bleibt CuloScribe strikt sachlich. Bei Community- und Kulturthemen ist ein Hauch Ironie erlaubt. Niemals albern. Niemals respektlos gegenüber der Berichterstattung, auf der CuloScribe aufbaut.',
    about_disclaimer_h: 'Redaktionelle Transparenz',
    about_disclaimer_p: 'Artikel auf CuloTon werden von einer KI-Redaktion (CuloScribe) verfasst, basierend auf öffentlich zugänglicher Berichterstattung Dritter. Wir sind nicht die Originalreporter. Wir sind eine redaktionelle Schicht, die TON-Nachrichten in einfacher Sprache in vier Sprachen nacherzählt — mit Quellenangabe und Link zum Original. Wenn Sie Rechteinhaber eines Originalartikels sind und ein Anliegen haben, kontaktieren Sie uns — wir antworten.',
    about_languages_h: 'Verfügbare Sprachen',
    about_languages_p: 'CuloTon erscheint auf Englisch, Russisch, Polnisch und Deutsch. Jede Version ist eine eigenständige Bearbeitung (keine maschinelle Übersetzung), die CuloScribe in einem redaktionellen Durchgang erstellt.',
    about_contact_p: 'Haben Sie einen Tipp, eine Story, die wir verpasst haben, oder möchten Werbung schalten? Schreiben Sie uns in der <a href="https://t.me/culoton">Telegram-Gruppe</a>.',
    date_label: '📅',
    source_label: '🗞',
    featured_token_pill: 'Featured Token',
    featured_token_h_html: 'Der native Token von CuloTon — <span class="ticker">$CULO</span>',
    featured_token_p: 'Ein Legacy-Memecoin mit Track Record auf Polygon (10,000X) und SUI — jetzt auf TON. Treibt diese Publikation und die Kultur rund um das Netzwerk an.',
    featured_token_btn_info: 'Token-Info',
    featured_token_btn_telegram: 'Telegram →',
    culo_title: '$CULO — der native Token von CuloTon',
    culo_meta_description: '$CULO ist ein Legacy-Memecoin, jetzt live auf TON. Multi-Chain-Track-Record: 10,000X auf Polygon, Erfolg auf SUI, jetzt zu Hause auf TON.',
    culo_summary: 'Ein Legacy-Memecoin — Multi-Chain-Veteran, jetzt live auf der TON-Blockchain.',
    culo_cta_join: 'Telegram beitreten →',
    culo_cta_view: 'Auf Tonviewer ansehen',
    culo_contract_label: 'Contract-Adresse (TON)',
    culo_copy: 'Kopieren',
    culo_copied: 'Kopiert!',
    culo_copy_failed: 'Kopieren fehlgeschlagen',
    culo_understanding_h: '$CULO auf TON — worum es geht',
    culo_understanding_p1_html: 'Culo ist ein Legacy-Meme, das seit Anfang 2024 mehrere Blockchains durchquert. Das Team erzielte einen phänomenalen <strong>10,000X-Anstieg der Marktkapitalisierung auf Polygon</strong> und zog dabei Namen wie <em>CryptosRUS, JAKE, RODNEY, Crypto Crow, Wendy O</em> sowie <em>WARREN SAPP</em> an — neben vielen anderen.',
    culo_understanding_p2_html: 'Das Projekt erzielte auch im <strong>SUI</strong>-Netzwerk bedeutende Erfolge und bewies seine Widerstandsfähigkeit über verschiedene Ökosysteme hinweg. Wir setzen jetzt denselben Weg massiven Wachstums auf <strong>TON</strong> fort — einschließlich des Starts dieser dedizierten Website und einer umfassenden Entwicklungs-Roadmap.',
    culo_track_h: 'Track Record',
    culo_track_li1_html: '<strong>2024 — Polygon:</strong> 10,000X-Anstieg der Marktkapitalisierung; Berichterstattung und Erwähnungen großer Krypto-KOLs',
    culo_track_li2_html: '<strong>SUI:</strong> starke Fortsetzung auf einer zweiten Chain — nachgewiesene Cross-Ecosystem-Traktion',
    culo_track_li3_html: '<strong>2026 — TON:</strong> Launch im Netzwerk mit nativer Telegram-Distribution und der CuloTon-Nachrichtenplattform',
    culo_why_h: 'Warum TON',
    culo_why_p: 'TON — The Open Network, ursprünglich von Telegram konzipiert — ist eine der am schnellsten wachsenden Blockchains der Jahre 2025-2026. Mit nativer Telegram-Integration, Sub-Sekunden-Finalität und einem rasch expandierenden Ökosystem aus Mini-Apps und DeFi-Protokollen ist TON einzigartig positioniert, um Krypto zu Hunderten Millionen Telegram-Nutzern zu bringen. $CULO kommt mit dem Schwung zweier vorheriger Chains und einer Community, die bereits weiß, wie man liefert.',
    culo_community_h: 'Community',
    culo_community_p_html: 'Am schnellsten beteiligen Sie sich über die offizielle Telegram-Gruppe: <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">https://t.me/culoton</a>. Nachrichten, Ankündigungen und Trade-Gespräche finden dort statt.',
    culo_disclaimer_h: 'Disclaimer',
    culo_disclaimer_p: 'Nichts auf dieser Seite stellt eine Finanzberatung dar. $CULO ist ein Memecoin; Kryptowährungen sind hochvolatil und Sie können Ihre gesamte Investition verlieren. Vergangene Performance auf Polygon oder SUI ist keine Garantie für zukünftige Ergebnisse auf TON oder einer anderen Chain. Recherchieren Sie stets selbst und kaufen Sie nur, was Sie sich zu verlieren leisten können. Die CuloTon-Berichterstattung ist redaktionell unabhängig von Token-Aktivitäten.',
    ecosystem_title: 'TON-Ökosystem-Karte — CuloTon',
    ecosystem_meta_description: 'Kuratierte Karte des TON-Ökosystems — Wallets, DEXes, NFT-Marktplätze, Mini-Apps, Infrastruktur und Foundation. Nur verifizierte Projekte.',
    ecosystem_kicker: 'CuloTon Desk · Ökosystem-Karte',
    ecosystem_h: 'Das TON-Ökosystem auf einen Blick',
    ecosystem_lede: (projects, categories) => `Eine kuratierte Karte der Projekte, die das TON-Netzwerk antreiben — was sie tun und wo man sie findet. ${projects} Projekte in ${categories} Kategorien. Redaktionelle Auswahl, kein bezahltes Verzeichnis.`,
    ecosystem_jump_label: 'Zur Kategorie springen',
    ecosystem_foot_h: 'Fehlt etwas oder ist etwas falsch?',
    ecosystem_foot_p_html: 'Diese Karte wird kuratiert — wir listen nur Projekte, die wir unabhängig prüfen können. Wenn Ihr Projekt hierhergehört oder ein Eintrag veraltet ist, melden Sie sich bei der Redaktion auf <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegram</a>. Keine bezahlten Platzierungen.',
    nav_apps: 'Mini-Apps',
    apps_title: 'TON Mini-Apps Hub — CuloTon',
    apps_meta_description: 'Kuratierter Hub für Telegram Mini Apps im TON-Orbit — Clicker, P2E-Spiele, Drop-Kampagnen, Sniper-Bots, NFT-Marktplätze. Nur verifizierte Telegram-Einstiegspunkte.',
    apps_kicker: 'CuloTon Desk · Mini-Apps-Hub',
    apps_h: 'Telegram Mini Apps auf TON',
    apps_lede: (apps, categories) => `Eine handverlesene Karte der Mini-Apps, die direkt in Telegram leben und auf TON abrechnen — Spiele, Drops, Sniper, NFTs. ${apps} Apps in ${categories} Kategorien. Redaktionelle Auswahl, keine bezahlten Plätze.`,
    apps_jump_label: 'Zur Kategorie springen',
    apps_open_in_telegram: 'In Telegram öffnen',
    apps_open_web: 'Website',
    apps_foot_h: 'Haben Sie eine App, die hier stehen sollte?',
    apps_foot_p_html: 'Wir nehmen nur Mini-Apps mit verifizierbarem Telegram-Einstiegspunkt und echter Nutzung. Wenn Ihr Projekt hierhergehört — oder ein Eintrag veraltet ist — melden Sie sich bei der Redaktion auf <a href="https://t.me/culoton" target="_blank" rel="noopener noreferrer">Telegram</a>. Keine bezahlten Platzierungen.',
  },
};

export function localizedPath(locale: Locale, path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  if (locale === 'en') return clean;
  return `/${locale}${clean === '/' ? '' : clean}`;
}

export function stripLocaleSlugFromId(id: string): string {
  return id.replace(/^(en|ru|pl|de)\//, '').replace(/\.md$/, '');
}
