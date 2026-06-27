import type { Locale } from '../i18n/strings';

export interface LaunchContent {
  meta_title: string;
  meta_description: string;
  status_kicker: string;
  status_pill: string;
  hero_h: string;
  hero_lede: string;
  hero_eta: string;
  cta_telegram: string;
  cta_telegram_blurb: string;

  why_h: string;
  why_lede: string;
  why_points: [string, string][];

  features_h: string;
  features: { icon: string; title: string; body: string }[];

  audit_h: string;
  audit_pill: string;
  audit_lede: string;
  audit_points: [string, string][];
  audit_foot: string;

  flow_h: string;
  flow_intro: string;
  flow_steps: { n: string; title: string; body: string }[];

  preview_h: string;
  preview_intro: string;
  preview_form_label_name: string;
  preview_form_ph_name: string;
  preview_form_label_symbol: string;
  preview_form_ph_symbol: string;
  preview_form_label_supply: string;
  preview_form_ph_supply: string;
  preview_form_label_decimals: string;
  preview_form_label_desc: string;
  preview_form_ph_desc: string;
  preview_form_label_logo: string;
  preview_form_logo_hint: string;
  preview_form_logo_choose: string;
  preview_form_label_revoke: string;
  preview_form_revoke_hint: string;
  preview_form_submit: string;
  preview_form_disabled_note: string;
  preview_caption: string;

  pricing_h: string;
  pricing_rows: { label: string; value: string; note?: string }[];
  pricing_disclaimer: string;

  wallets_h: string;
  wallets_blurb: string;
  wallets: string[];

  faq_h: string;
  faq: { q: string; a: string }[];

  cta_bottom_h: string;
  cta_bottom_p: string;
  cta_bottom_btn: string;

  disclaimer: string;
}

const EN: LaunchContent = {
  meta_title: 'BRAINROT Launcher — Deploy your GRAM jetton in 60 seconds',
  meta_description: 'Coming soon: the easiest way to deploy a GRAM jetton — upload logo, edit metadata anytime, or renounce ownership for permanent on-chain trust. No code, no install.',
  status_kicker: 'BRAINROT Desk · Building now',
  status_pill: '🚧 In development',
  hero_h: 'BRAINROT Launcher',
  hero_lede: 'Deploy your own GRAM jetton in under a minute — name it, give it a logo, choose your supply, and ship it on-chain. Edit metadata later if you want, or renounce ownership for permanent trust. No CLI, no Solidity, no smart-contract degree.',
  hero_eta: 'Public testnet target: end of May 2026 · Mainnet: when audits and dry-runs clear.',
  cta_telegram: 'Get notified on Telegram',
  cta_telegram_blurb: 'We post every milestone in the chat. Join to be first when testnet opens.',

  why_h: 'Why we’re building this',
  why_lede: 'Deploying a jetton on GRAM today means either trusting a half-built dapp inside a wallet, copy-pasting commands from a GitHub README, or paying someone to do it. We think it should take 60 seconds in a browser, with logo upload, edit and revoke baked in.',
  why_points: [
    ['Niche is wide open', 'Standalone web jetton-launchers with logo upload, editable metadata and a clean revoke flow barely exist. The few that do are bare and ugly. The audience already trusts BRAINROT for GRAM-ecosystem coverage — this is the natural next step.'],
    ['No middlemen, no custody', 'We never touch your funds or your token. Your wallet signs the deploy transaction directly to the GRAM network. We get a small service fee in the same transaction — fully on-chain, fully transparent.'],
    ['Open source', 'Code lives on github.com/CuloTon, audited contracts only (TEP-74 reference jetton master). You can read every line that touches the deploy.'],
  ],

  features_h: 'What you’ll get',
  features: [
    { icon: '🚀', title: 'One-click jetton deploy', body: 'Fill a 5-field form, sign once in your wallet, get a live jetton address with explorer link. The contract is the audited TEP-74 reference jetton master — same standard Tonkeeper, STON.fi and DeDust use.' },
    { icon: '🎨', title: 'Logo upload to IPFS', body: 'Drag in a PNG, JPG or WEBP. We pin it to IPFS so the image is content-addressed and survives even if our domain dies. Metadata JSON follows TEP-64 — readable by every GRAM wallet and explorer.' },
    { icon: '✍️', title: 'Edit metadata later', body: 'Want to fix a typo in the description, swap the logo, or update the website link? As long as you keep ownership, you can push a new metadata URI from the manage panel. Token contract stays the same — only the off-chain content updates.' },
    { icon: '🔒', title: 'Renounce ownership', body: 'One transaction sets admin to the null address. After that, nobody — including you — can mint more, change metadata, or transfer admin. Supply becomes hard-capped on-chain. Strong trust signal for holders, and a one-click move when you’re ready.' },
  ],

  audit_h: 'Audited contract — already',
  audit_pill: '✅ Audit done',
  audit_lede: 'The deploy doesn’t use our own smart contract. It uses the official TEP-74 Jetton Master maintained by the GRAM Foundation — the same contract that USDT-GRAM, Notcoin ($NOT), most STON.fi listings and the majority of major GRAM tokens run on. Independent audits and years of mainnet use have already happened. We don’t modify a single byte of it.',
  audit_points: [
    ['Audited by Trail of Bits + Certik + GRAM Foundation core team', 'The reference jetton master in github.com/ton-blockchain/token-contract has been audited multiple times before mainnet — by Trail of Bits, Certik and reviewed internally by the GRAM core dev team. Findings are public, all fixes are merged into the upstream contract you’re deploying.'],
    ['Battle-tested by USDT and Notcoin', 'USDT-GRAM ($2 B+ supply) and Notcoin ($NOT — 100 B+ supply) both run on exactly this jetton master. Years of mainnet operation, billions in volume settled, zero contract-level incidents. Strongest social-proof audit a GRAM contract has.'],
    ['We wrap, we don’t modify', 'BRAINROT Launcher only prepares the deploy transaction (constructor data + your metadata URI + your service-fee message) and hands it to your wallet. Your wallet, your signature, official bytecode. No fork, no custom logic, no surprises.'],
    ['Open-source frontend', 'The launcher UI itself is on github.com/CuloTon/culoton — anyone can read the exact transaction we build for the wallet. No hidden message slipped into the deploy. Same scrutiny you’d give a CLI script.'],
  ],
  audit_foot: 'Translation: when you click Deploy, you are not trusting BRAINROT code with your tokens. You are deploying the same contract that USDT and Notcoin live on — we’re just the form that fills it in for you.',

  flow_h: 'How it works',
  flow_intro: 'End-to-end in your browser, no installs, no signups. Your wallet is the only account.',
  flow_steps: [
    { n: '01', title: 'Fill the form', body: 'Name, symbol, total supply, decimals (default 9), description, logo. Live preview shows exactly how the token will appear in Tonkeeper.' },
    { n: '02', title: 'Connect your wallet', body: 'TonConnect modal — pick Tonkeeper, MyTonWallet, Bitget, OpenMask or any TonConnect-compatible wallet. No seed phrase touches our page.' },
    { n: '03', title: 'Sign one transaction', body: 'Your wallet shows the full transaction: deploy fee (≈0.5–1 GRAM gas) plus our service fee. Approve once. The GRAM network confirms in ~10 seconds.' },
    { n: '04', title: 'Token is live', body: 'You land on a manage page with your jetton address, explorer link, mint button, edit-metadata button and a renounce button. Share the address, list it on DEXes, or revoke when you’re ready.' },
  ],

  preview_h: 'A taste of the UI',
  preview_intro: 'Below is a non-functional mockup of the deploy form — pixel-accurate to what we’re building. Fields are disabled until testnet opens.',
  preview_form_label_name: 'Token name',
  preview_form_ph_name: 'e.g. BRAINROT Forever',
  preview_form_label_symbol: 'Symbol',
  preview_form_ph_symbol: 'e.g. CULOFOR',
  preview_form_label_supply: 'Total supply',
  preview_form_ph_supply: 'e.g. 1000000000',
  preview_form_label_decimals: 'Decimals',
  preview_form_label_desc: 'Description (optional)',
  preview_form_ph_desc: 'A short pitch — shown in wallets and explorers.',
  preview_form_label_logo: 'Logo',
  preview_form_logo_hint: 'PNG, JPG or WEBP · up to 200 KB · pinned to IPFS',
  preview_form_logo_choose: 'Choose file…',
  preview_form_label_revoke: 'Renounce ownership at deploy?',
  preview_form_revoke_hint: 'Off by default. You can renounce later from the manage panel.',
  preview_form_submit: 'Deploy jetton',
  preview_form_disabled_note: 'Form is locked until public testnet — this is a preview only.',
  preview_caption: 'Light theme example. The live form will match the rest of BRAINROT — same fonts, same dark/terminal feel.',

  pricing_h: 'Pricing',
  pricing_rows: [
    { label: 'GRAM network gas (paid to validators)', value: '≈ 0.5–1 GRAM', note: 'one-time per deploy' },
    { label: 'IPFS pinning for logo + metadata', value: 'free', note: 'covered by us' },
    { label: 'BRAINROT service fee', value: 'TBA', note: 'small flat fee per deploy — final number announced before launch' },
    { label: 'Edit metadata (post-deploy)', value: '≈ 0.05 GRAM gas', note: 'only if you stay admin' },
    { label: 'Renounce ownership', value: '≈ 0.05 GRAM gas', note: 'one-time, irreversible' },
  ],
  pricing_disclaimer: 'You always pay gas directly to the GRAM network through your own wallet. The service fee is bundled in the same transaction and goes to the BRAINROT treasury — used to fund the news desk and the weekly community prize pool.',

  wallets_h: 'Works with every TonConnect wallet',
  wallets_blurb: 'No accounts, no extensions to install — TonConnect is the open standard for GRAM apps. Anything in your wallet stays in your wallet.',
  wallets: ['Tonkeeper', 'MyTonWallet', 'Tonhub', 'Bitget Wallet', 'OpenMask', 'Wallet (Telegram)'],

  faq_h: 'FAQ',
  faq: [
    { q: 'Will my token be a real GRAM jetton?', a: 'Yes — full TEP-74 / TEP-89 compliance. It will show up in Tonkeeper, on tonviewer, tonscan, GeckoTerminal, STON.fi, DeDust — anywhere that supports GRAM jettons.' },
    { q: 'Do you take a cut of the supply?', a: 'No. 100% of the supply mints to your wallet. Our only fee is the small flat amount bundled in the deploy transaction.' },
    { q: 'Can I delete a jetton I deployed?', a: 'No — that’s how blockchains work. You can burn supply you own, and you can renounce ownership to lock the contract forever. The contract itself is permanent.' },
    { q: 'What about the logo if your site goes down?', a: 'The logo and metadata live on IPFS, content-addressed. Even if brainrot-ton.fun disappears tomorrow, your jetton still shows correctly in every wallet — GRAM wallets can fetch IPFS directly.' },
    { q: 'Is it safe to use?', a: 'The smart contract is the audited TEP-74 reference jetton master maintained by the GRAM Foundation — used by USDT, NOT and most major GRAM tokens. The launcher itself just packages the deploy transaction for your wallet to sign. We hold nothing.' },
    { q: 'When does it go live?', a: 'Public testnet aimed at end of May 2026. Mainnet after a round of community testing and a security review. Sign up for updates via the Telegram chat.' },
  ],

  cta_bottom_h: 'Be first in line',
  cta_bottom_p: 'Join the Telegram chat to get a ping the second testnet opens. Early users get the lowest service-fee tier for the first 100 deployments.',
  cta_bottom_btn: 'Join the BRAINROT chat',

  disclaimer: 'BRAINROT Launcher does not offer financial advice, custody your funds, or vet the tokens deployed through it. Anyone can deploy a token on GRAM — verify before you trust or buy. The renounce-ownership feature is irreversible by design.',
};

const RU: LaunchContent = {
  meta_title: 'BRAINROT Launcher — деплой GRAM-jetton за 60 секунд',
  meta_description: 'Скоро: самый простой способ задеплоить GRAM-jetton — загрузка логотипа, редактирование метаданных в любой момент или отказ от владения для постоянного on-chain доверия. Без кода и установок.',
  status_kicker: 'BRAINROT Desk · Строим прямо сейчас',
  status_pill: '🚧 В разработке',
  hero_h: 'BRAINROT Launcher',
  hero_lede: 'Задеплой собственный GRAM-jetton меньше чем за минуту — назови, дай логотип, выбери supply и отправь в сеть. Хочешь — отредактируй метаданные позже, или откажись от владения для бессрочного доверия. Без CLI, без Solidity, без диплома по смарт-контрактам.',
  hero_eta: 'Цель публичного testnet — конец мая 2026. Mainnet — после аудитов и прогонов.',
  cta_telegram: 'Узнать о запуске в Telegram',
  cta_telegram_blurb: 'Каждый этап постим в чат. Подпишись — первым попадёшь на testnet.',

  why_h: 'Зачем мы это строим',
  why_lede: 'Задеплоить jetton на GRAM сегодня — это либо доверять полуготовому dapp внутри кошелька, либо копипастить команды из README на GitHub, либо платить кому-то. Мы считаем, что это должно занимать 60 секунд в браузере, с загрузкой логотипа, правкой и revoke встроенными.',
  why_points: [
    ['Ниша открыта', 'Standalone веб-лаунчеров jetton’ов с загрузкой логотипа, редактируемыми метаданными и нормальным revoke практически нет. Те что есть — голые и страшные. Аудитория BRAINROT уже доверяет нам по освещению экосистемы GRAM — это логичный следующий шаг.'],
    ['Без посредников, без кастодии', 'Мы не касаемся ваших средств и токена. Ваш кошелёк сам подписывает транзакцию деплоя в сеть GRAM. Мы получаем небольшую сервисную комиссию в той же транзакции — полностью on-chain, полностью прозрачно.'],
    ['Open source', 'Код лежит на github.com/CuloTon, контракты — только аудированные (референсный TEP-74 jetton master). Можно прочитать каждую строчку, которая касается деплоя.'],
  ],

  features_h: 'Что вы получите',
  features: [
    { icon: '🚀', title: 'Деплой jetton в один клик', body: 'Заполни форму из 5 полей, подпиши в кошельке — получи живой адрес jetton со ссылкой на эксплорер. Контракт — аудированный референсный TEP-74 jetton master, тот же стандарт, что у Tonkeeper, STON.fi и DeDust.' },
    { icon: '🎨', title: 'Логотип на IPFS', body: 'Перетащи PNG, JPG или WEBP. Пиним на IPFS, картинка адресуется по содержимому и переживёт даже падение нашего домена. Metadata JSON по TEP-64 — читается каждым GRAM-кошельком и эксплорером.' },
    { icon: '✍️', title: 'Правка метаданных потом', body: 'Хочешь исправить опечатку в описании, поменять лого или обновить ссылку на сайт? Пока ты остаёшься админом — можно отправить новый metadata URI из manage-панели. Контракт тот же, обновляется только off-chain контент.' },
    { icon: '🔒', title: 'Отказ от владения', body: 'Одна транзакция выставляет admin в null-адрес. После этого никто — включая тебя — не может минтить, менять метаданные или передавать админа. Supply закрепляется on-chain. Сильный сигнал доверия для холдеров — и одна кнопка, когда будешь готов.' },
  ],

  audit_h: 'Контракт уже аудирован',
  audit_pill: '✅ Аудит сделан',
  audit_lede: 'Деплой не использует наш собственный смарт-контракт. Используется официальный TEP-74 Jetton Master, поддерживаемый GRAM Foundation — тот же контракт, на котором работают USDT-GRAM, Notcoin ($NOT), большинство листингов STON.fi и львиная доля крупных GRAM-токенов. Независимые аудиты и годы работы в mainnet уже произошли. Мы не меняем ни байта.',
  audit_points: [
    ['Аудитили Trail of Bits + Certik + core-команда GRAM Foundation', 'Референсный jetton master в github.com/ton-blockchain/token-contract прошёл несколько аудитов до mainnet — Trail of Bits, Certik плюс внутренний ревью core-команды GRAM. Отчёты публичны, все фиксы вмёрджены в upstream-контракт, который вы деплоите.'],
    ['Проверен USDT и Notcoin на практике', 'USDT-GRAM ($2+ млрд supply) и Notcoin ($NOT — 100+ млрд supply) работают именно на этом jetton master. Годы mainnet-эксплуатации, миллиарды оборота, ноль инцидентов на уровне контракта. Самая сильная социальная аудит-проверка, какая у GRAM-контракта может быть.'],
    ['Мы оборачиваем, не модифицируем', 'BRAINROT Launcher только готовит транзакцию деплоя (данные конструктора + ваш URI метаданных + сообщение сервисной комиссии) и передаёт её в кошелёк. Ваш кошелёк, ваша подпись, официальный байт-код. Никаких форков, никакой кастомной логики, никаких сюрпризов.'],
    ['Open source фронтенд', 'Сам UI лаунчера лежит на github.com/CuloTon/culoton — любой может прочитать, какую транзакцию мы передаём в кошелёк. Никаких скрытых сообщений в деплое. Та же проверка, что вы бы дали CLI-скрипту.'],
  ],
  audit_foot: 'Перевод: когда вы нажимаете Deploy, вы НЕ доверяете свои токены коду BRAINROT. Вы деплоите тот же контракт, на котором живут USDT и Notcoin — мы просто форма, которая его за вас заполняет.',

  flow_h: 'Как это работает',
  flow_intro: 'Весь путь — в браузере, без установок и регистраций. Кошелёк — твой единственный аккаунт.',
  flow_steps: [
    { n: '01', title: 'Заполни форму', body: 'Имя, символ, total supply, decimals (по умолчанию 9), описание, логотип. Live preview показывает, как токен будет выглядеть в Tonkeeper.' },
    { n: '02', title: 'Подключи кошелёк', body: 'Модалка TonConnect — выбери Tonkeeper, MyTonWallet, Bitget, OpenMask или любой совместимый. Сид-фраза нашу страницу даже не видит.' },
    { n: '03', title: 'Подпиши одну транзакцию', body: 'Кошелёк показывает всё: газ деплоя (≈0.5–1 GRAM) плюс наша сервисная комиссия. Подтверди один раз. Сеть GRAM подтверждает за ~10 секунд.' },
    { n: '04', title: 'Токен в сети', body: 'Попадаешь на manage-страницу: адрес jetton, ссылка на эксплорер, кнопки mint / edit metadata / renounce. Делись адресом, листингуй на DEX, или revoke когда готов.' },
  ],

  preview_h: 'Как будет выглядеть UI',
  preview_intro: 'Ниже — нерабочий макет формы деплоя, pixel-accurate к тому что строим. Поля заблокированы до открытия testnet.',
  preview_form_label_name: 'Имя токена',
  preview_form_ph_name: 'например, BRAINROT Forever',
  preview_form_label_symbol: 'Тикер',
  preview_form_ph_symbol: 'например, CULOFOR',
  preview_form_label_supply: 'Total supply',
  preview_form_ph_supply: 'например, 1000000000',
  preview_form_label_decimals: 'Decimals',
  preview_form_label_desc: 'Описание (необязательно)',
  preview_form_ph_desc: 'Короткий питч — показывается в кошельках и эксплорерах.',
  preview_form_label_logo: 'Логотип',
  preview_form_logo_hint: 'PNG, JPG или WEBP · до 200 КБ · пиним на IPFS',
  preview_form_logo_choose: 'Выбрать файл…',
  preview_form_label_revoke: 'Отказаться от владения при деплое?',
  preview_form_revoke_hint: 'По умолчанию выкл. Можно отказаться позже из manage-панели.',
  preview_form_submit: 'Деплой jetton',
  preview_form_disabled_note: 'Форма заблокирована до публичного testnet — это пока только превью.',
  preview_caption: 'Пример со светлой темой. Финальная форма будет в стиле остального BRAINROT — те же шрифты, тот же terminal-look.',

  pricing_h: 'Цены',
  pricing_rows: [
    { label: 'Газ сети GRAM (валидаторам)', value: '≈ 0.5–1 GRAM', note: 'один раз за деплой' },
    { label: 'Пин IPFS для логотипа и метаданных', value: 'бесплатно', note: 'покрываем мы' },
    { label: 'Сервисная комиссия BRAINROT', value: 'TBA', note: 'небольшой fix per deploy — финальную цифру объявим перед запуском' },
    { label: 'Правка метаданных (после деплоя)', value: '≈ 0.05 GRAM газ', note: 'только пока ты админ' },
    { label: 'Отказ от владения', value: '≈ 0.05 GRAM газ', note: 'один раз, необратимо' },
  ],
  pricing_disclaimer: 'Газ всегда платится напрямую сети GRAM через ваш кошелёк. Сервисная комиссия идёт в той же транзакции в казну BRAINROT — на финансирование редакции и еженедельного призового фонда сообщества.',

  wallets_h: 'Работает с любым TonConnect-кошельком',
  wallets_blurb: 'Никаких аккаунтов и расширений — TonConnect это открытый стандарт для GRAM-приложений. Всё что лежит в вашем кошельке — там и остаётся.',
  wallets: ['Tonkeeper', 'MyTonWallet', 'Tonhub', 'Bitget Wallet', 'OpenMask', 'Wallet (Telegram)'],

  faq_h: 'FAQ',
  faq: [
    { q: 'Это будет настоящий GRAM jetton?', a: 'Да — полное соответствие TEP-74 / TEP-89. Покажется в Tonkeeper, на tonviewer, tonscan, GeckoTerminal, STON.fi, DeDust — везде, где поддерживаются GRAM jetton’ы.' },
    { q: 'Вы забираете долю supply?', a: 'Нет. 100% supply минтится в ваш кошелёк. Наша единственная плата — небольшой fix в транзакции деплоя.' },
    { q: 'Можно удалить jetton, который я задеплоил?', a: 'Нет — так работают блокчейны. Можно сжечь часть supply, которой владеешь, и можно отказаться от владения, чтобы навсегда заблокировать контракт. Сам контракт постоянный.' },
    { q: 'Что с логотипом, если ваш сайт упадёт?', a: 'Логотип и метаданные на IPFS, адресуются по содержимому. Даже если brainrot-ton.fun исчезнет завтра — jetton всё равно правильно отображается в каждом кошельке. GRAM-кошельки умеют ходить в IPFS напрямую.' },
    { q: 'Это безопасно?', a: 'Смарт-контракт — аудированный референсный TEP-74 jetton master от GRAM Foundation, тот же что у USDT, NOT и большинства крупных GRAM-токенов. Лаунчер только собирает транзакцию для подписи в вашем кошельке. Ничего у нас не хранится.' },
    { q: 'Когда запуск?', a: 'Публичный testnet — цель конец мая 2026. Mainnet — после раунда тестов сообществом и обзора безопасности. Подпишись на апдейты через Telegram-чат.' },
  ],

  cta_bottom_h: 'Будь первым',
  cta_bottom_p: 'Заходи в Telegram-чат, чтобы получить пинг в ту же секунду, как testnet откроется. Ранние пользователи получат самый низкий тариф сервисной комиссии на первые 100 деплоев.',
  cta_bottom_btn: 'В чат BRAINROT',

  disclaimer: 'BRAINROT Launcher не даёт финансовых советов, не хранит ваши средства и не проверяет токены, задеплоенные через него. Задеплоить токен на GRAM может кто угодно — проверяйте перед тем, как доверять или покупать. Функция отказа от владения необратима по дизайну.',
};

const PL: LaunchContent = {
  meta_title: 'BRAINROT Launcher — wdróż swój jetton GRAM w 60 sekund',
  meta_description: 'Wkrótce: najprostszy sposób na deploy jettona GRAM — wgranie logo, edycja metadanych w każdej chwili, lub renounce ownership dla trwałego on-chain zaufania. Bez kodu i instalek.',
  status_kicker: 'BRAINROT Desk · Budujemy właśnie',
  status_pill: '🚧 W budowie',
  hero_h: 'BRAINROT Launcher',
  hero_lede: 'Wdróż własnego jettona GRAM w niecałą minutę — nazwij go, daj logo, wybierz supply i wyślij on-chain. Edytuj metadane później, jeśli chcesz, albo zrzeknij się własności dla trwałego zaufania. Bez CLI, bez Solidity, bez dyplomu z smart contractów.',
  hero_eta: 'Cel publicznego testnetu: koniec maja 2026. Mainnet: po audytach i przejazdach próbnych.',
  cta_telegram: 'Powiadom mnie na Telegramie',
  cta_telegram_blurb: 'Każdy kamień milowy postujemy w czacie. Dołącz i bądź pierwszy gdy testnet ruszy.',

  why_h: 'Po co to budujemy',
  why_lede: 'Deploy jettona na GRAM dziś to albo zaufanie półgotowej dappce wewnątrz portfela, albo kopiowanie komend z README na GitHubie, albo płacenie komuś. Naszym zdaniem powinno to zająć 60 sekund w przeglądarce, z wgraniem logo, edycją i revoke w pakiecie.',
  why_points: [
    ['Nisza jest otwarta', 'Standalone webowych launcherów jettonów z wgraniem logo, edytowalnymi metadanymi i czystym revoke prawie nie ma. Te które są — surowe i brzydkie. Publiczność BRAINROT już ufa nam w newsach o ekosystemie GRAM — to naturalny następny krok.'],
    ['Bez pośredników, bez custody', 'Nigdy nie dotykamy twoich środków ani tokena. Twój portfel sam podpisuje transakcję deployu prosto do sieci GRAM. My dostajemy małą prowizję w tej samej transakcji — w pełni on-chain, w pełni transparentnie.'],
    ['Open source', 'Kod jest na github.com/CuloTon, kontrakty — tylko audytowane (referencyjny TEP-74 jetton master). Możesz przeczytać każdą linijkę, która dotyka deployu.'],
  ],

  features_h: 'Co dostajesz',
  features: [
    { icon: '🚀', title: 'Deploy jettona jednym kliknięciem', body: 'Wypełnij 5-polowy formularz, podpisz raz w portfelu, dostań żywy adres jettona z linkiem do eksploratora. Kontrakt to audytowany referencyjny TEP-74 jetton master — ten sam standard co u Tonkeepera, STON.fi i DeDust.' },
    { icon: '🎨', title: 'Logo na IPFS', body: 'Wrzuć PNG, JPG lub WEBP. Pinujemy na IPFS, więc obrazek jest adresowany po treści i przeżyje nawet padnięcie naszej domeny. Metadata JSON wg TEP-64 — czytane przez każdy portfel i eksplorator GRAM.' },
    { icon: '✍️', title: 'Edycja metadanych później', body: 'Chcesz poprawić literówkę w opisie, podmienić logo, zaktualizować link do strony? Dopóki zostajesz adminem, możesz pchnąć nowy URI metadanych z panelu manage. Kontrakt zostaje, zmienia się tylko zawartość off-chain.' },
    { icon: '🔒', title: 'Zrzeknięcie się własności (renounce)', body: 'Jedna transakcja ustawia admina na null. Po tym nikt — łącznie z tobą — nie może domintować, zmienić metadanych ani przekazać admina. Supply zostaje hard-capped on-chain. Mocny sygnał zaufania dla holderów — i jeden klik, kiedy jesteś gotowy.' },
  ],

  audit_h: 'Kontrakt jest już zaudytowany',
  audit_pill: '✅ Audyt zrobiony',
  audit_lede: 'Deploy nie używa naszego własnego smart kontraktu. Korzysta z oficjalnego TEP-74 Jetton Master utrzymywanego przez GRAM Foundation — tego samego kontraktu, na którym działa USDT-GRAM, Notcoin ($NOT), większość listingów na STON.fi i znaczna część dużych tokenów GRAM. Niezależne audyty i lata pracy na mainnecie już za nim. Nie zmieniamy ani jednego bajtu.',
  audit_points: [
    ['Audyt: Trail of Bits + Certik + core team GRAM Foundation', 'Referencyjny jetton master w github.com/ton-blockchain/token-contract przeszedł wiele audytów przed mainnetem — Trail of Bits, Certik plus wewnętrzny review core teamu GRAM. Raporty są publiczne, wszystkie fixy są zmerge’owane do upstream kontraktu, który wdrażasz.'],
    ['Sprawdzony przez USDT i Notcoin w praktyce', 'USDT-GRAM (>2 mld $ supply) i Notcoin ($NOT — >100 mld supply) działają dokładnie na tym jetton master. Lata pracy na mainnecie, miliardy wolumenu, zero incydentów na poziomie kontraktu. Najmocniejszy społeczny stempel jakości jaki kontrakt GRAM może mieć.'],
    ['My owijamy, nie modyfikujemy', 'BRAINROT Launcher tylko przygotowuje transakcję deployu (dane konstruktora + twój URI metadanych + wiadomość z prowizją serwisową) i przekazuje ją do portfela. Twój portfel, twoja sygnatura, oficjalny bytecode. Bez forka, bez własnej logiki, bez niespodzianek.'],
    ['Frontend open source', 'Sam UI launchera leży na github.com/CuloTon/culoton — każdy może przeczytać dokładnie jaką transakcję budujemy dla portfela. Żadnej ukrytej wiadomości wciśniętej do deployu. Ta sama kontrola jaką dałbyś skryptowi CLI.'],
  ],
  audit_foot: 'Tłumaczenie: kiedy klikasz Deploy, NIE powierzasz swoich tokenów kodowi BRAINROT. Wdrażasz dokładnie ten sam kontrakt, na którym żyją USDT i Notcoin — my jesteśmy tylko formularzem, który go za ciebie wypełnia.',

  flow_h: 'Jak to działa',
  flow_intro: 'Całość w przeglądarce, bez instalek i rejestracji. Portfel to twoje jedyne konto.',
  flow_steps: [
    { n: '01', title: 'Wypełnij formularz', body: 'Nazwa, symbol, total supply, decimals (domyślnie 9), opis, logo. Live preview pokazuje dokładnie jak token będzie wyglądał w Tonkeeperze.' },
    { n: '02', title: 'Podłącz portfel', body: 'Modal TonConnect — wybierz Tonkeeper, MyTonWallet, Bitget, OpenMask albo dowolny zgodny portfel. Twoja seed phrase nie dotyka naszej strony.' },
    { n: '03', title: 'Podpisz jedną transakcję', body: 'Portfel pokazuje pełną transakcję: gas deployu (≈0.5–1 GRAM) plus nasza prowizja serwisowa. Zatwierdź raz. Sieć GRAM potwierdza w ~10 sekund.' },
    { n: '04', title: 'Token jest live', body: 'Lądujesz na stronie manage z adresem jettona, linkiem do eksploratora, przyciskiem mint, edytuj metadane i renounce. Dziel się adresem, listuj na DEX-ach, albo revoke gdy gotowy.' },
  ],

  preview_h: 'Jak będzie wyglądać',
  preview_intro: 'Poniżej niedziałający mockup formularza deployu — pixel-accurate do tego co budujemy. Pola są zablokowane do otwarcia testnetu.',
  preview_form_label_name: 'Nazwa tokena',
  preview_form_ph_name: 'np. BRAINROT Forever',
  preview_form_label_symbol: 'Symbol',
  preview_form_ph_symbol: 'np. CULOFOR',
  preview_form_label_supply: 'Total supply',
  preview_form_ph_supply: 'np. 1000000000',
  preview_form_label_decimals: 'Decimals',
  preview_form_label_desc: 'Opis (opcjonalnie)',
  preview_form_ph_desc: 'Krótki pitch — pokazany w portfelach i eksploratorach.',
  preview_form_label_logo: 'Logo',
  preview_form_logo_hint: 'PNG, JPG lub WEBP · do 200 KB · pinowane na IPFS',
  preview_form_logo_choose: 'Wybierz plik…',
  preview_form_label_revoke: 'Zrzec się własności przy deployu?',
  preview_form_revoke_hint: 'Domyślnie wyłączone. Możesz revoke później z panelu manage.',
  preview_form_submit: 'Deploy jetton',
  preview_form_disabled_note: 'Formularz jest zablokowany do publicznego testnetu — to na razie tylko podgląd.',
  preview_caption: 'Przykład z jasną teką. Finalny formularz będzie pasował do reszty BRAINROT — te same fonty, ten sam terminal-look.',

  pricing_h: 'Ceny',
  pricing_rows: [
    { label: 'Gas sieci GRAM (idzie do walidatorów)', value: '≈ 0.5–1 GRAM', note: 'jednorazowo za deploy' },
    { label: 'IPFS pinning dla logo + metadanych', value: 'darmo', note: 'pokrywamy my' },
    { label: 'Prowizja serwisowa BRAINROT', value: 'TBA', note: 'mała flat fee za deploy — finalna kwota ogłoszona przed startem' },
    { label: 'Edycja metadanych (po deployu)', value: '≈ 0.05 GRAM gas', note: 'tylko jeśli zostajesz adminem' },
    { label: 'Renounce ownership', value: '≈ 0.05 GRAM gas', note: 'jednorazowo, nieodwracalnie' },
  ],
  pricing_disclaimer: 'Gas zawsze płacisz bezpośrednio do sieci GRAM, przez swój portfel. Prowizja serwisowa idzie w tej samej transakcji do skarbca BRAINROT — wykorzystywana na finansowanie redakcji i tygodniowej puli nagród dla społeczności.',

  wallets_h: 'Działa z każdym portfelem TonConnect',
  wallets_blurb: 'Bez kont, bez wtyczek do instalowania — TonConnect to otwarty standard aplikacji GRAM. Co masz w portfelu, zostaje w portfelu.',
  wallets: ['Tonkeeper', 'MyTonWallet', 'Tonhub', 'Bitget Wallet', 'OpenMask', 'Wallet (Telegram)'],

  faq_h: 'FAQ',
  faq: [
    { q: 'Czy mój token będzie prawdziwym jettonem GRAM?', a: 'Tak — pełna zgodność z TEP-74 / TEP-89. Pokaże się w Tonkeeperze, na tonviewer, tonscan, GeckoTerminal, STON.fi, DeDust — wszędzie tam gdzie wspierane są jettony GRAM.' },
    { q: 'Bierzecie kawałek supply?', a: 'Nie. 100% supply mintuje się do twojego portfela. Nasza jedyna opłata to mała flat fee dorzucona do transakcji deployu.' },
    { q: 'Czy mogę usunąć jettona którego wdrożyłem?', a: 'Nie — tak działają blockchainy. Możesz spalić część supply którą posiadasz, i możesz zrzec się własności, żeby zamknąć kontrakt na zawsze. Sam kontrakt jest permanentny.' },
    { q: 'A co z logo jeśli wasza strona padnie?', a: 'Logo i metadane lezą na IPFS, adresowane po treści. Nawet jeśli brainrot-ton.fun zniknie jutro, twój jetton dalej pokazuje się poprawnie w każdym portfelu. Portfele GRAM potrafią chodzić do IPFS bezpośrednio.' },
    { q: 'Czy to bezpieczne?', a: 'Smart kontrakt to audytowany referencyjny TEP-74 jetton master utrzymywany przez GRAM Foundation — używany przez USDT, NOT i większość dużych tokenów GRAM. Sam launcher tylko pakuje transakcję deployu do podpisu w twoim portfelu. U nas nic nie zostaje.' },
    { q: 'Kiedy startuje?', a: 'Publiczny testnet — cel koniec maja 2026. Mainnet po rundzie testów społecznościowych i przeglądzie bezpieczeństwa. Zapisz się na aktualizacje przez Telegram chat.' },
  ],

  cta_bottom_h: 'Bądź pierwszy w kolejce',
  cta_bottom_p: 'Dołącz do Telegram chatu, żeby dostać ping w sekundę kiedy testnet ruszy. Wcześni użytkownicy dostają najniższy tier prowizji na pierwsze 100 deployów.',
  cta_bottom_btn: 'Dołącz do chatu BRAINROT',

  disclaimer: 'BRAINROT Launcher nie udziela porad finansowych, nie przechowuje twoich środków i nie weryfikuje tokenów wdrożonych przez niego. Każdy może wdrożyć token na GRAM — sprawdź zanim zaufasz lub kupisz. Funkcja renounce ownership jest nieodwracalna by design.',
};

const DE: LaunchContent = {
  meta_title: 'BRAINROT Launcher — GRAM-Jetton in 60 Sekunden deployen',
  meta_description: 'Bald: der einfachste Weg, ein GRAM-Jetton zu deployen — Logo hochladen, Metadaten jederzeit ändern oder Ownership unwiderruflich abgeben für dauerhaftes On-Chain-Vertrauen. Kein Code, keine Installation.',
  status_kicker: 'BRAINROT Desk · Wir bauen jetzt',
  status_pill: '🚧 In Entwicklung',
  hero_h: 'BRAINROT Launcher',
  hero_lede: 'Deploye dein eigenes GRAM-Jetton in unter einer Minute — Name, Logo, Supply wählen und auf die Kette schicken. Metadaten später bearbeiten, oder Ownership für dauerhaftes Vertrauen abgeben. Kein CLI, kein Solidity, kein Smart-Contract-Diplom.',
  hero_eta: 'Public Testnet Ziel: Ende Mai 2026. Mainnet: nach Audits und Probedurchläufen.',
  cta_telegram: 'Per Telegram benachrichtigen',
  cta_telegram_blurb: 'Wir posten jeden Meilenstein im Chat. Tritt bei und sei der Erste, wenn das Testnet öffnet.',

  why_h: 'Warum wir das bauen',
  why_lede: 'Heute ein Jetton auf GRAM zu deployen heißt: einem halbfertigen dApp im Wallet vertrauen, Befehle aus einem GitHub-README kopieren oder jemanden bezahlen. Wir finden, das sollte 60 Sekunden im Browser dauern — mit Logo-Upload, Bearbeitung und Revoke eingebaut.',
  why_points: [
    ['Nische offen', 'Eigenständige Web-Jetton-Launcher mit Logo-Upload, editierbaren Metadaten und sauberem Revoke-Flow gibt es kaum. Die wenigen existierenden sind nackt und hässlich. Das BRAINROT-Publikum vertraut uns schon bei GRAM-Berichterstattung — das ist der natürliche nächste Schritt.'],
    ['Keine Vermittler, keine Verwahrung', 'Wir berühren nie eure Mittel oder Token. Eure Wallet signiert die Deploy-Transaktion direkt ans GRAM-Netzwerk. Wir bekommen eine kleine Service-Gebühr in derselben Transaktion — vollständig on-chain, vollständig transparent.'],
    ['Open Source', 'Code lebt auf github.com/CuloTon, Kontrakte nur audited (TEP-74 Referenz-Jetton-Master). Jede Zeile, die Deploy berührt, ist lesbar.'],
  ],

  features_h: 'Was du bekommst',
  features: [
    { icon: '🚀', title: 'Ein-Klick-Jetton-Deploy', body: 'Fülle ein 5-Felder-Formular, unterschreibe einmal im Wallet, bekomme eine Live-Jetton-Adresse mit Explorer-Link. Der Kontrakt ist der audited TEP-74 Referenz-Jetton-Master — derselbe Standard wie bei Tonkeeper, STON.fi und DeDust.' },
    { icon: '🎨', title: 'Logo auf IPFS', body: 'Zieh PNG, JPG oder WEBP rein. Wir pinnen auf IPFS, das Bild ist inhalts-adressiert und überlebt auch, wenn unsere Domain stirbt. Metadata-JSON nach TEP-64 — lesbar von jedem GRAM-Wallet und Explorer.' },
    { icon: '✍️', title: 'Metadaten später bearbeiten', body: 'Tippfehler in der Beschreibung korrigieren, Logo tauschen, Website-Link aktualisieren? Solange du Owner bist, kannst du im Manage-Panel eine neue Metadata-URI pushen. Token-Kontrakt bleibt gleich — nur der Off-Chain-Inhalt aktualisiert.' },
    { icon: '🔒', title: 'Ownership abgeben (Renounce)', body: 'Eine Transaktion setzt den Admin auf die Null-Adresse. Danach kann niemand — auch du nicht — mehr minten, Metadaten ändern oder Admin übertragen. Supply wird on-chain hart gedeckelt. Starkes Vertrauenssignal für Halter — und ein Klick, wenn du soweit bist.' },
  ],

  audit_h: 'Kontrakt ist bereits auditiert',
  audit_pill: '✅ Audit erledigt',
  audit_lede: 'Der Deploy nutzt nicht unseren eigenen Smart Contract. Er nutzt den offiziellen TEP-74 Jetton Master, gepflegt von der GRAM Foundation — denselben Kontrakt, auf dem USDT-GRAM, Notcoin ($NOT), die meisten STON.fi-Listings und der Großteil großer GRAM-Token laufen. Unabhängige Audits und Jahre Mainnet-Betrieb sind bereits passiert. Wir ändern kein Byte daran.',
  audit_points: [
    ['Auditiert von Trail of Bits + Certik + GRAM Foundation Core-Team', 'Der Referenz-Jetton-Master in github.com/ton-blockchain/token-contract wurde vor Mainnet mehrfach auditiert — von Trail of Bits, Certik und intern vom GRAM-Core-Team reviewt. Befunde sind öffentlich, alle Fixes sind in den Upstream-Kontrakt gemergt, den du deployst.'],
    ['Battle-tested durch USDT und Notcoin', 'USDT-GRAM (>2 Mrd. $ Supply) und Notcoin ($NOT — >100 Mrd. Supply) laufen genau auf diesem Jetton Master. Jahre Mainnet-Betrieb, Milliarden Volumen abgewickelt, null Vorfälle auf Kontraktebene. Stärkster sozialer Audit-Stempel, den ein GRAM-Kontrakt haben kann.'],
    ['Wir umhüllen, wir modifizieren nicht', 'BRAINROT Launcher bereitet nur die Deploy-Transaktion vor (Konstruktordaten + deine Metadata-URI + Service-Fee-Message) und übergibt sie deinem Wallet. Dein Wallet, deine Signatur, offizieller Bytecode. Kein Fork, keine eigene Logik, keine Überraschungen.'],
    ['Open-Source-Frontend', 'Die Launcher-UI selbst liegt auf github.com/CuloTon/culoton — jeder kann die genaue Transaktion lesen, die wir fürs Wallet bauen. Keine versteckte Message im Deploy. Dieselbe Prüfung, die du einem CLI-Skript geben würdest.'],
  ],
  audit_foot: 'Übersetzt: wenn du auf Deploy klickst, vertraust du deine Token NICHT dem BRAINROT-Code an. Du deployst denselben Kontrakt, auf dem USDT und Notcoin leben — wir sind nur das Formular, das ihn für dich ausfüllt.',

  flow_h: 'Wie es funktioniert',
  flow_intro: 'Alles im Browser, keine Installationen, keine Anmeldungen. Dein Wallet ist dein einziger Account.',
  flow_steps: [
    { n: '01', title: 'Formular ausfüllen', body: 'Name, Symbol, Total Supply, Decimals (Standard 9), Beschreibung, Logo. Live-Vorschau zeigt genau, wie der Token in Tonkeeper aussieht.' },
    { n: '02', title: 'Wallet verbinden', body: 'TonConnect-Modal — Tonkeeper, MyTonWallet, Bitget, OpenMask oder jedes kompatible Wallet. Deine Seed-Phrase berührt unsere Seite nie.' },
    { n: '03', title: 'Eine Transaktion signieren', body: 'Wallet zeigt die volle Transaktion: Deploy-Gas (≈0.5–1 GRAM) plus unsere Service-Gebühr. Einmal bestätigen. GRAM-Netzwerk bestätigt in ~10 Sekunden.' },
    { n: '04', title: 'Token ist live', body: 'Du landest auf einer Manage-Seite mit Jetton-Adresse, Explorer-Link, Mint-Button, Edit-Metadaten-Button und Renounce-Button. Adresse teilen, auf DEXes listen, oder revoken wenn du soweit bist.' },
  ],

  preview_h: 'So wird die UI aussehen',
  preview_intro: 'Darunter ein nicht-funktionales Mockup des Deploy-Formulars — pixelgenau zu dem, was wir bauen. Felder sind gesperrt bis das Testnet öffnet.',
  preview_form_label_name: 'Token-Name',
  preview_form_ph_name: 'z. B. BRAINROT Forever',
  preview_form_label_symbol: 'Symbol',
  preview_form_ph_symbol: 'z. B. CULOFOR',
  preview_form_label_supply: 'Total Supply',
  preview_form_ph_supply: 'z. B. 1000000000',
  preview_form_label_decimals: 'Decimals',
  preview_form_label_desc: 'Beschreibung (optional)',
  preview_form_ph_desc: 'Kurzer Pitch — wird in Wallets und Explorern angezeigt.',
  preview_form_label_logo: 'Logo',
  preview_form_logo_hint: 'PNG, JPG oder WEBP · bis 200 KB · auf IPFS gepinnt',
  preview_form_logo_choose: 'Datei wählen…',
  preview_form_label_revoke: 'Ownership beim Deploy gleich abgeben?',
  preview_form_revoke_hint: 'Standardmäßig aus. Du kannst auch später im Manage-Panel abgeben.',
  preview_form_submit: 'Jetton deployen',
  preview_form_disabled_note: 'Formular ist gesperrt bis zum Public Testnet — das ist nur eine Vorschau.',
  preview_caption: 'Light-Theme-Beispiel. Das Live-Formular wird zum Rest von BRAINROT passen — gleiche Fonts, gleiche Terminal-Optik.',

  pricing_h: 'Preise',
  pricing_rows: [
    { label: 'GRAM-Netzwerk-Gas (an Validatoren)', value: '≈ 0,5–1 GRAM', note: 'einmalig pro Deploy' },
    { label: 'IPFS-Pinning für Logo + Metadaten', value: 'kostenlos', note: 'übernehmen wir' },
    { label: 'BRAINROT Service-Gebühr', value: 'TBA', note: 'kleine flat fee pro Deploy — finaler Betrag vor Launch angekündigt' },
    { label: 'Metadaten bearbeiten (nach Deploy)', value: '≈ 0,05 GRAM Gas', note: 'nur solange du Admin bist' },
    { label: 'Ownership abgeben', value: '≈ 0,05 GRAM Gas', note: 'einmalig, unwiderruflich' },
  ],
  pricing_disclaimer: 'Gas zahlst du immer direkt ans GRAM-Netzwerk über dein eigenes Wallet. Die Service-Gebühr ist in derselben Transaktion gebündelt und geht an die BRAINROT-Treasury — finanziert die News-Redaktion und den wöchentlichen Community-Preispool.',

  wallets_h: 'Funktioniert mit jedem TonConnect-Wallet',
  wallets_blurb: 'Keine Konten, keine Erweiterungen zum Installieren — TonConnect ist der offene Standard für GRAM-Apps. Alles, was in deinem Wallet ist, bleibt in deinem Wallet.',
  wallets: ['Tonkeeper', 'MyTonWallet', 'Tonhub', 'Bitget Wallet', 'OpenMask', 'Wallet (Telegram)'],

  faq_h: 'FAQ',
  faq: [
    { q: 'Wird mein Token ein echter GRAM-Jetton sein?', a: 'Ja — vollständige TEP-74 / TEP-89 Konformität. Erscheint in Tonkeeper, auf tonviewer, tonscan, GeckoTerminal, STON.fi, DeDust — überall, wo GRAM-Jettons unterstützt werden.' },
    { q: 'Nehmt ihr einen Anteil am Supply?', a: 'Nein. 100% des Supply mintet in dein Wallet. Unsere einzige Gebühr ist der kleine Festbetrag in der Deploy-Transaktion.' },
    { q: 'Kann ich einen deployten Jetton löschen?', a: 'Nein — so funktionieren Blockchains. Du kannst Supply, den du besitzt, verbrennen, und du kannst Ownership abgeben, um den Kontrakt für immer zu sperren. Der Kontrakt selbst ist permanent.' },
    { q: 'Was passiert mit dem Logo, wenn eure Seite ausfällt?', a: 'Logo und Metadaten leben auf IPFS, inhalts-adressiert. Selbst wenn brainrot-ton.fun morgen verschwindet, zeigt dein Jetton in jedem Wallet weiterhin korrekt — GRAM-Wallets können IPFS direkt abrufen.' },
    { q: 'Ist es sicher zu nutzen?', a: 'Der Smart Contract ist der audited TEP-74 Referenz-Jetton-Master der GRAM Foundation — verwendet von USDT, NOT und den meisten großen GRAM-Tokens. Der Launcher packt nur die Deploy-Transaktion für dein Wallet zum Signieren. Wir halten nichts.' },
    { q: 'Wann geht es live?', a: 'Public Testnet Ziel Ende Mai 2026. Mainnet nach einer Runde Community-Tests und Sicherheitsprüfung. Melde dich für Updates via Telegram-Chat an.' },
  ],

  cta_bottom_h: 'Sei als Erster dabei',
  cta_bottom_p: 'Tritt dem Telegram-Chat bei, um einen Ping in der Sekunde zu bekommen, in der das Testnet öffnet. Frühe Nutzer bekommen die niedrigste Service-Gebühr-Stufe für die ersten 100 Deployments.',
  cta_bottom_btn: 'In den BRAINROT-Chat',

  disclaimer: 'BRAINROT Launcher bietet keine Finanzberatung, verwahrt eure Mittel nicht und prüft die deployten Token nicht. Jeder kann einen Token auf GRAM deployen — prüft, bevor ihr vertraut oder kauft. Die Renounce-Funktion ist by design unwiderruflich.',
};

const ES: LaunchContent = {
  meta_title: 'BRAINROT Launcher — despliega tu jetton de GRAM en 60 segundos',
  meta_description: 'Próximamente: la forma más fácil de desplegar un jetton de GRAM — subir logo, editar metadatos cuando quieras, o renunciar a la propiedad para confianza permanente on-chain. Sin código, sin instalaciones.',
  status_kicker: 'BRAINROT Desk · Construyendo ahora',
  status_pill: '🚧 En desarrollo',
  hero_h: 'BRAINROT Launcher',
  hero_lede: 'Despliega tu propio jetton de GRAM en menos de un minuto — ponle nombre, dale un logo, elige el supply y mándalo on-chain. Edita los metadatos después si quieres, o renuncia a la propiedad para confianza permanente. Sin CLI, sin Solidity, sin título en smart contracts.',
  hero_eta: 'Objetivo de testnet pública: finales de mayo de 2026. Mainnet: cuando pasen auditorías y pruebas.',
  cta_telegram: 'Avísame por Telegram',
  cta_telegram_blurb: 'Publicamos cada hito en el chat. Únete para ser el primero cuando abra el testnet.',

  why_h: 'Por qué lo construimos',
  why_lede: 'Desplegar un jetton en GRAM hoy significa confiar en una dapp a medio hacer dentro de una billetera, copiar comandos de un README de GitHub, o pagar a alguien. Creemos que debería tomar 60 segundos en un navegador, con subida de logo, edición y revoke incluidos.',
  why_points: [
    ['Nicho abierto', 'Launchers de jetton web independientes con subida de logo, metadatos editables y un flujo de revoke limpio apenas existen. Los pocos que hay son pelados y feos. La audiencia de BRAINROT ya confía en nosotros para cobertura del ecosistema GRAM — este es el siguiente paso natural.'],
    ['Sin intermediarios, sin custodia', 'Nunca tocamos tus fondos ni tu token. Tu billetera firma la transacción de despliegue directamente a la red GRAM. Recibimos una pequeña comisión de servicio en la misma transacción — totalmente on-chain, totalmente transparente.'],
    ['Open source', 'El código vive en github.com/CuloTon, contratos solo auditados (referencia TEP-74 jetton master). Puedes leer cada línea que toca el despliegue.'],
  ],

  features_h: 'Lo que obtienes',
  features: [
    { icon: '🚀', title: 'Despliegue de jetton en un clic', body: 'Rellena un formulario de 5 campos, firma una vez en tu billetera, obtén una dirección de jetton viva con enlace al explorer. El contrato es el TEP-74 jetton master de referencia auditado — el mismo estándar que usan Tonkeeper, STON.fi y DeDust.' },
    { icon: '🎨', title: 'Logo en IPFS', body: 'Arrastra un PNG, JPG o WEBP. Lo pineamos en IPFS, así la imagen se direcciona por contenido y sobrevive incluso si nuestro dominio cae. JSON de metadatos sigue TEP-64 — leíble por toda billetera y explorer de GRAM.' },
    { icon: '✍️', title: 'Editar metadatos después', body: '¿Quieres corregir una errata en la descripción, cambiar el logo, actualizar el enlace de la web? Mientras mantengas la propiedad, puedes empujar una nueva URI de metadatos desde el panel de gestión. El contrato del token sigue igual — solo se actualiza el contenido off-chain.' },
    { icon: '🔒', title: 'Renunciar a la propiedad', body: 'Una transacción pone el admin a la dirección nula. Después, nadie — incluido tú — puede mintear más, cambiar metadatos ni transferir admin. El supply queda fijado on-chain. Señal fuerte de confianza para los holders — y un clic cuando estés listo.' },
  ],

  audit_h: 'El contrato ya está auditado',
  audit_pill: '✅ Auditoría hecha',
  audit_lede: 'El despliegue no usa nuestro propio smart contract. Usa el TEP-74 Jetton Master oficial mantenido por la GRAM Foundation — el mismo contrato que ejecutan USDT-GRAM, Notcoin ($NOT), la mayoría de listings en STON.fi y la gran mayoría de los tokens grandes de GRAM. Auditorías independientes y años de uso en mainnet ya han ocurrido. No modificamos ni un byte.',
  audit_points: [
    ['Auditado por Trail of Bits + Certik + core team de GRAM Foundation', 'El jetton master de referencia en github.com/ton-blockchain/token-contract ha sido auditado varias veces antes de mainnet — por Trail of Bits, Certik y revisado internamente por el core team de GRAM. Los hallazgos son públicos, todos los fixes están mergeados en el contrato upstream que despliegas.'],
    ['Probado en combate por USDT y Notcoin', 'USDT-GRAM (>2 mil M$ de supply) y Notcoin ($NOT — >100 mil M de supply) corren exactamente sobre este jetton master. Años de operación en mainnet, miles de millones en volumen, cero incidentes a nivel de contrato. El sello social de auditoría más fuerte que un contrato GRAM puede tener.'],
    ['Envolvemos, no modificamos', 'BRAINROT Launcher solo prepara la transacción de despliegue (datos del constructor + tu URI de metadatos + mensaje de comisión de servicio) y la entrega a tu billetera. Tu billetera, tu firma, bytecode oficial. Sin fork, sin lógica propia, sin sorpresas.'],
    ['Frontend open source', 'La UI del launcher en sí está en github.com/CuloTon/culoton — cualquiera puede leer la transacción exacta que armamos para la billetera. Ningún mensaje oculto colado en el despliegue. El mismo escrutinio que le darías a un script CLI.'],
  ],
  audit_foot: 'Traducción: cuando haces clic en Desplegar, NO le confías tus tokens al código de BRAINROT. Despliegas el mismo contrato sobre el que viven USDT y Notcoin — nosotros somos solo el formulario que lo rellena por ti.',

  flow_h: 'Cómo funciona',
  flow_intro: 'Todo en tu navegador, sin instalaciones, sin registros. Tu billetera es tu única cuenta.',
  flow_steps: [
    { n: '01', title: 'Rellena el formulario', body: 'Nombre, símbolo, total supply, decimals (por defecto 9), descripción, logo. La vista previa en vivo muestra exactamente cómo aparecerá el token en Tonkeeper.' },
    { n: '02', title: 'Conecta tu billetera', body: 'Modal TonConnect — elige Tonkeeper, MyTonWallet, Bitget, OpenMask o cualquier billetera compatible. Tu seed phrase no toca nuestra página.' },
    { n: '03', title: 'Firma una transacción', body: 'La billetera muestra la transacción completa: gas de despliegue (≈0.5–1 GRAM) más nuestra comisión de servicio. Aprueba una vez. La red GRAM confirma en ~10 segundos.' },
    { n: '04', title: 'El token está vivo', body: 'Llegas a una página de gestión con la dirección del jetton, enlace al explorer, botón de mint, botón de editar metadatos y botón de renounce. Comparte la dirección, lista en DEX, o revoca cuando estés listo.' },
  ],

  preview_h: 'Una probadita del UI',
  preview_intro: 'Abajo hay un mockup no funcional del formulario de despliegue — pixel-accurate a lo que estamos construyendo. Los campos están deshabilitados hasta que abra el testnet.',
  preview_form_label_name: 'Nombre del token',
  preview_form_ph_name: 'p. ej. BRAINROT Forever',
  preview_form_label_symbol: 'Símbolo',
  preview_form_ph_symbol: 'p. ej. CULOFOR',
  preview_form_label_supply: 'Total supply',
  preview_form_ph_supply: 'p. ej. 1000000000',
  preview_form_label_decimals: 'Decimals',
  preview_form_label_desc: 'Descripción (opcional)',
  preview_form_ph_desc: 'Un pitch corto — se muestra en billeteras y exploradores.',
  preview_form_label_logo: 'Logo',
  preview_form_logo_hint: 'PNG, JPG o WEBP · hasta 200 KB · pineado a IPFS',
  preview_form_logo_choose: 'Elegir archivo…',
  preview_form_label_revoke: '¿Renunciar a la propiedad al desplegar?',
  preview_form_revoke_hint: 'Desactivado por defecto. Puedes renunciar después desde el panel de gestión.',
  preview_form_submit: 'Desplegar jetton',
  preview_form_disabled_note: 'El formulario está bloqueado hasta el testnet público — esto es solo una vista previa.',
  preview_caption: 'Ejemplo con tema claro. El formulario en vivo coincidirá con el resto de BRAINROT — mismas tipografías, mismo aire terminal.',

  pricing_h: 'Precios',
  pricing_rows: [
    { label: 'Gas de red GRAM (a validadores)', value: '≈ 0.5–1 GRAM', note: 'una vez por despliegue' },
    { label: 'Pinning IPFS para logo + metadatos', value: 'gratis', note: 'corre por nuestra cuenta' },
    { label: 'Comisión de servicio BRAINROT', value: 'TBA', note: 'pequeña tarifa fija por despliegue — número final anunciado antes del lanzamiento' },
    { label: 'Editar metadatos (post-despliegue)', value: '≈ 0.05 GRAM gas', note: 'solo si sigues siendo admin' },
    { label: 'Renunciar a la propiedad', value: '≈ 0.05 GRAM gas', note: 'una vez, irreversible' },
  ],
  pricing_disclaimer: 'Siempre pagas el gas directamente a la red GRAM a través de tu propia billetera. La comisión de servicio va en la misma transacción y entra en la treasury de BRAINROT — se usa para financiar la redacción y el premio comunitario semanal.',

  wallets_h: 'Funciona con cualquier billetera TonConnect',
  wallets_blurb: 'Sin cuentas, sin extensiones que instalar — TonConnect es el estándar abierto para apps de GRAM. Lo que está en tu billetera se queda en tu billetera.',
  wallets: ['Tonkeeper', 'MyTonWallet', 'Tonhub', 'Bitget Wallet', 'OpenMask', 'Wallet (Telegram)'],

  faq_h: 'FAQ',
  faq: [
    { q: '¿Mi token será un jetton real de GRAM?', a: 'Sí — cumplimiento completo TEP-74 / TEP-89. Aparecerá en Tonkeeper, en tonviewer, tonscan, GeckoTerminal, STON.fi, DeDust — donde sea que se soporten jettons de GRAM.' },
    { q: '¿Os quedáis con parte del supply?', a: 'No. El 100% del supply se mintea en tu billetera. Nuestra única comisión es la pequeña tarifa fija incluida en la transacción de despliegue.' },
    { q: '¿Puedo borrar un jetton que desplegué?', a: 'No — así funcionan las blockchains. Puedes quemar supply que posees, y puedes renunciar a la propiedad para bloquear el contrato para siempre. El contrato en sí es permanente.' },
    { q: '¿Qué pasa con el logo si vuestro sitio se cae?', a: 'El logo y los metadatos viven en IPFS, direccionados por contenido. Incluso si brainrot-ton.fun desaparece mañana, tu jetton se sigue mostrando correctamente en cada billetera — las billeteras GRAM pueden ir a IPFS directamente.' },
    { q: '¿Es seguro usarlo?', a: 'El smart contract es el TEP-74 jetton master de referencia auditado mantenido por la GRAM Foundation — usado por USDT, NOT y la mayoría de los tokens grandes de GRAM. El launcher solo empaqueta la transacción de despliegue para que tu billetera la firme. No retenemos nada.' },
    { q: '¿Cuándo sale?', a: 'Testnet público apunta a finales de mayo de 2026. Mainnet tras una ronda de pruebas comunitarias y revisión de seguridad. Apúntate a actualizaciones por el chat de Telegram.' },
  ],

  cta_bottom_h: 'Sé el primero',
  cta_bottom_p: 'Únete al chat de Telegram para recibir un ping en el segundo en que abra el testnet. Los usuarios tempranos consiguen el tier de comisión más bajo para los primeros 100 despliegues.',
  cta_bottom_btn: 'Únete al chat de BRAINROT',

  disclaimer: 'BRAINROT Launcher no ofrece asesoramiento financiero, no custodia tus fondos ni examina los tokens desplegados a través de él. Cualquiera puede desplegar un token en GRAM — verifica antes de confiar o comprar. La función de renounce ownership es irreversible por diseño.',
};

const UK: LaunchContent = {
  meta_title: 'BRAINROT Launcher — деплой GRAM-джетона за 60 секунд',
  meta_description: 'Незабаром: найпростіший спосіб задеплоїти GRAM-джетон — завантаження логотипа, редагування метаданих будь-коли, або відмова від володіння для постійної довіри on-chain. Без коду й установок.',
  status_kicker: 'BRAINROT Desk · Будуємо зараз',
  status_pill: '🚧 У розробці',
  hero_h: 'BRAINROT Launcher',
  hero_lede: 'Задеплой власний GRAM-джетон менш ніж за хвилину — назви його, додай лого, обери supply й відправ on-chain. Хочеш — редагуй метадані потім, або відмовся від володіння для безстрокової довіри. Без CLI, без Solidity, без диплома зі смарт-контрактів.',
  hero_eta: 'Ціль публічного testnet — кінець травня 2026. Mainnet — після аудитів і прогонів.',
  cta_telegram: 'Сповістити в Telegram',
  cta_telegram_blurb: 'Кожну віху постимо в чат. Приєднуйся — будеш першим, коли відкриється testnet.',

  why_h: 'Навіщо ми це будуємо',
  why_lede: 'Задеплоїти джетон на GRAM сьогодні — це або довіряти напівготовому dapp всередині гаманця, або копіпастити команди з README на GitHub, або платити комусь. Ми вважаємо, що це має займати 60 секунд у браузері, із завантаженням лого, редагуванням і revoke у комплекті.',
  why_points: [
    ['Ніша відкрита', 'Самостійні веб-лаунчери джетонів із завантаженням лого, редагованими метаданими й нормальним revoke майже не існують. Ті що є — голі й страшні. Аудиторія BRAINROT уже довіряє нам по освітленню екосистеми GRAM — це логічний наступний крок.'],
    ['Без посередників, без кастоді', 'Ми ніколи не торкаємося ваших коштів і токена. Ваш гаманець сам підписує транзакцію деплою прямо в мережу GRAM. Ми отримуємо невелику сервісну комісію в тій самій транзакції — повністю on-chain, повністю прозоро.'],
    ['Open source', 'Код лежить на github.com/CuloTon, контракти — лише аудитовані (референсний TEP-74 jetton master). Можна прочитати кожен рядок, який торкається деплою.'],
  ],

  features_h: 'Що ви отримаєте',
  features: [
    { icon: '🚀', title: 'Деплой джетона в один клік', body: 'Заповни форму з 5 полів, підпиши в гаманці — отримай живу адресу джетона з посиланням на експлорер. Контракт — аудитований референсний TEP-74 jetton master, той самий стандарт, що в Tonkeeper, STON.fi і DeDust.' },
    { icon: '🎨', title: 'Лого на IPFS', body: 'Перетягни PNG, JPG або WEBP. Пінимо на IPFS, картинка адресується за вмістом і переживе навіть падіння нашого домену. Metadata JSON за TEP-64 — читається кожним GRAM-гаманцем і експлорером.' },
    { icon: '✍️', title: 'Редагування метаданих пізніше', body: 'Хочеш виправити друкарську помилку в описі, замінити лого або оновити посилання на сайт? Поки ти лишаєшся адміном — можна відправити новий metadata URI з manage-панелі. Контракт лишається той самий, оновлюється тільки off-chain контент.' },
    { icon: '🔒', title: 'Відмова від володіння', body: 'Одна транзакція виставляє admin у null-адресу. Після цього ніхто — включаючи тебе — не може мінтити, змінювати метадані чи передавати адмін. Supply фіксується on-chain. Сильний сигнал довіри для холдерів — і одна кнопка, коли будеш готовий.' },
  ],

  audit_h: 'Контракт уже аудитований',
  audit_pill: '✅ Аудит зроблено',
  audit_lede: 'Деплой не використовує наш власний смарт-контракт. Використовується офіційний TEP-74 Jetton Master, який підтримує GRAM Foundation — той самий контракт, на якому працюють USDT-GRAM, Notcoin ($NOT), більшість лістингів STON.fi і левова частка великих GRAM-токенів. Незалежні аудити й роки роботи в mainnet уже відбулися. Ми не змінюємо жодного байта.',
  audit_points: [
    ['Аудит: Trail of Bits + Certik + core-команда GRAM Foundation', 'Референсний jetton master у github.com/ton-blockchain/token-contract пройшов кілька аудитів перед mainnet — Trail of Bits, Certik плюс внутрішнє ревʼю core-команди GRAM. Звіти публічні, всі фікси злиті в upstream-контракт, який ви деплоїте.'],
    ['Перевірений на бою USDT і Notcoin', 'USDT-GRAM (>2 млрд $ supply) і Notcoin ($NOT — >100 млрд supply) працюють саме на цьому jetton master. Роки mainnet-експлуатації, мільярди обороту, нуль інцидентів на рівні контракту. Найсильніший соціальний штамп аудиту, який GRAM-контракт може мати.'],
    ['Ми обгортаємо, не модифікуємо', 'BRAINROT Launcher тільки готує транзакцію деплою (дані конструктора + ваш URI метаданих + повідомлення сервісної комісії) і передає її гаманцю. Ваш гаманець, ваш підпис, офіційний байткод. Без форка, без власної логіки, без сюрпризів.'],
    ['Open source фронтенд', 'Сам UI лаунчера лежить на github.com/CuloTon/culoton — будь-хто може прочитати, яку саме транзакцію ми збираємо для гаманця. Жодного прихованого повідомлення в деплої. Та сама перевірка, яку ви дали б CLI-скрипту.'],
  ],
  audit_foot: 'Переклад: коли ви натискаєте Deploy, ви НЕ довіряєте свої токени коду BRAINROT. Ви деплоїте той самий контракт, на якому живуть USDT і Notcoin — ми лише форма, що його за вас заповнює.',

  flow_h: 'Як це працює',
  flow_intro: 'Весь шлях — у браузері, без установок і реєстрацій. Гаманець — твій єдиний акаунт.',
  flow_steps: [
    { n: '01', title: 'Заповни форму', body: 'Ім\'я, символ, total supply, decimals (за замовчуванням 9), опис, лого. Live preview показує, як токен виглядатиме в Tonkeeper.' },
    { n: '02', title: 'Підключи гаманець', body: 'Модалка TonConnect — вибери Tonkeeper, MyTonWallet, Bitget, OpenMask або будь-який сумісний. Сід-фраза нашу сторінку навіть не бачить.' },
    { n: '03', title: 'Підпиши одну транзакцію', body: 'Гаманець показує все: газ деплою (≈0.5–1 GRAM) плюс наша сервісна комісія. Підтверди один раз. Мережа GRAM підтверджує за ~10 секунд.' },
    { n: '04', title: 'Токен у мережі', body: 'Потрапляєш на manage-сторінку: адреса джетона, посилання на експлорер, кнопки mint / edit metadata / renounce. Ділись адресою, лістингуй на DEX, або revoke коли готовий.' },
  ],

  preview_h: 'Як виглядатиме UI',
  preview_intro: 'Нижче — нефункціональний мокап форми деплою, pixel-accurate до того що будуємо. Поля заблоковані до відкриття testnet.',
  preview_form_label_name: 'Ім\'я токена',
  preview_form_ph_name: 'напр. BRAINROT Forever',
  preview_form_label_symbol: 'Тикер',
  preview_form_ph_symbol: 'напр. CULOFOR',
  preview_form_label_supply: 'Total supply',
  preview_form_ph_supply: 'напр. 1000000000',
  preview_form_label_decimals: 'Decimals',
  preview_form_label_desc: 'Опис (необов\'язково)',
  preview_form_ph_desc: 'Короткий пітч — показується в гаманцях і експлорерах.',
  preview_form_label_logo: 'Лого',
  preview_form_logo_hint: 'PNG, JPG або WEBP · до 200 КБ · пінимо на IPFS',
  preview_form_logo_choose: 'Вибрати файл…',
  preview_form_label_revoke: 'Відмовитись від володіння при деплої?',
  preview_form_revoke_hint: 'За замовчуванням вимкнено. Можна відмовитись пізніше з manage-панелі.',
  preview_form_submit: 'Деплой джетона',
  preview_form_disabled_note: 'Форма заблокована до публічного testnet — це поки лише превʼю.',
  preview_caption: 'Приклад зі світлою темою. Фінальна форма буде у стилі решти BRAINROT — ті самі шрифти, той самий terminal-look.',

  pricing_h: 'Ціни',
  pricing_rows: [
    { label: 'Газ мережі GRAM (валідаторам)', value: '≈ 0,5–1 GRAM', note: 'разово за деплой' },
    { label: 'IPFS pinning для лого + метаданих', value: 'безкоштовно', note: 'покриваємо ми' },
    { label: 'Сервісна комісія BRAINROT', value: 'TBA', note: 'невеликий fix per deploy — фінальну цифру оголосимо перед запуском' },
    { label: 'Редагування метаданих (після деплою)', value: '≈ 0,05 GRAM газ', note: 'тільки поки ти адмін' },
    { label: 'Відмова від володіння', value: '≈ 0,05 GRAM газ', note: 'разово, незворотно' },
  ],
  pricing_disclaimer: 'Газ завжди платиться напряму мережі GRAM через ваш гаманець. Сервісна комісія йде в тій самій транзакції в скарбницю BRAINROT — на фінансування редакції та щотижневого призового фонду спільноти.',

  wallets_h: 'Працює з будь-яким TonConnect-гаманцем',
  wallets_blurb: 'Жодних акаунтів і розширень — TonConnect це відкритий стандарт для GRAM-застосунків. Все що у вашому гаманці — там і лишається.',
  wallets: ['Tonkeeper', 'MyTonWallet', 'Tonhub', 'Bitget Wallet', 'OpenMask', 'Wallet (Telegram)'],

  faq_h: 'FAQ',
  faq: [
    { q: 'Це буде справжній GRAM джетон?', a: 'Так — повна відповідність TEP-74 / TEP-89. З\'явиться в Tonkeeper, на tonviewer, tonscan, GeckoTerminal, STON.fi, DeDust — скрізь, де підтримуються GRAM джетони.' },
    { q: 'Ви забираєте частину supply?', a: 'Ні. 100% supply мінтиться у ваш гаманець. Наша єдина плата — невеликий fix у транзакції деплою.' },
    { q: 'Можна видалити джетон, який я задеплоїв?', a: 'Ні — так працюють блокчейни. Можна спалити частину supply, якою володієте, і можна відмовитись від володіння, щоб назавжди заблокувати контракт. Сам контракт постійний.' },
    { q: 'А що з лого, якщо ваш сайт впаде?', a: 'Лого й метадані на IPFS, адресуються за вмістом. Навіть якщо brainrot-ton.fun зникне завтра — джетон все одно правильно відображається в кожному гаманці. GRAM-гаманці вміють ходити в IPFS напряму.' },
    { q: 'Це безпечно?', a: 'Смарт-контракт — аудитований референсний TEP-74 jetton master від GRAM Foundation, той самий що в USDT, NOT і більшості великих GRAM-токенів. Лаунчер тільки збирає транзакцію для підпису у вашому гаманці. Нічого в нас не зберігається.' },
    { q: 'Коли запуск?', a: 'Публічний testnet — ціль кінець травня 2026. Mainnet — після раунду тестів спільнотою й огляду безпеки. Підпишіться на апдейти через Telegram-чат.' },
  ],

  cta_bottom_h: 'Будь першим',
  cta_bottom_p: 'Заходь у Telegram-чат, щоб отримати пінг в ту саму секунду, як testnet відкриється. Ранні користувачі отримають найнижчий тариф сервісної комісії на перші 100 деплоїв.',
  cta_bottom_btn: 'У чат BRAINROT',

  disclaimer: 'BRAINROT Launcher не дає фінансових порад, не зберігає ваші кошти й не перевіряє токени, задеплоєні через нього. Задеплоїти токен на GRAM може будь-хто — перевіряйте перш ніж довіряти чи купувати. Функція відмови від володіння незворотна за дизайном.',
};

export const LAUNCH: Record<Locale, LaunchContent> = {
  en: EN,
  ru: RU,
  pl: PL,
  de: DE,
  es: ES,
  uk: UK,
};
