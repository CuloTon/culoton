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
  nav_about: string;
  nav_token: string;
  footer_tagline_html: string;
  footer_about: string;
  footer_token: string;
  footer_telegram: string;
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
    nav_about: 'About',
    nav_token: '$CULO',
    footer_tagline_html: '<strong>CuloTon</strong> — TON ecosystem news, powered by <span class="footer-ticker">$CULO</span>',
    footer_about: 'About',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
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
    nav_about: 'О проекте',
    nav_token: '$CULO',
    footer_tagline_html: '<strong>CuloTon</strong> — новости экосистемы TON, на базе <span class="footer-ticker">$CULO</span>',
    footer_about: 'О проекте',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
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
    nav_about: 'O nas',
    nav_token: '$CULO',
    footer_tagline_html: '<strong>CuloTon</strong> — wiadomości z ekosystemu TON, napędzane przez <span class="footer-ticker">$CULO</span>',
    footer_about: 'O nas',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
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
    nav_about: 'Über uns',
    nav_token: '$CULO',
    footer_tagline_html: '<strong>CuloTon</strong> — Nachrichten aus dem TON-Ökosystem, powered by <span class="footer-ticker">$CULO</span>',
    footer_about: 'Über uns',
    footer_token: '$CULO',
    footer_telegram: 'Telegram',
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
