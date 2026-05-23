export type PollLocale = 'en' | 'pl' | 'de' | 'ru' | 'es' | 'uk';

export interface PollStrings {
  pageTitle: string;
  metaDescription: string;
  kicker: string;
  h1: string;
  intro: string[];
  noRefundNote: string;

  q1Label: string;
  q1Keep: string;
  q1KeepDesc: string;
  q1New: string;
  q1NewDesc: string;

  q2Label: string;
  q2Tax: string;
  q2TaxDesc: string;
  q2NoTax: string;
  q2NoTaxDesc: string;

  buyLabel: string;
  sellLabel: string;
  splitLabel: string;
  splitOptions: Record<string, string>;

  tickerLabel: string;
  tickerHint: string;
  tickerPlaceholder: string;

  submit: string;
  submitting: string;
  alreadyVoted: string;
  thanks: string;
  errorGeneric: string;

  resultsH: string;
  resultsBlurb: string;
  resultsLoading: string;
  resultsTotal: (n: number) => string;
  resultsEmpty: string;
  resultsTickers: string;
  resultsTickersEmpty: string;
  resultsTaxBreakdown: string;
  resultsSplitBreakdown: string;
  refreshAuto: string;
}

const PCT = (n: number) => `${n}%`;

export const POLL_STRINGS: Record<PollLocale, PollStrings> = {
  en: {
    pageTitle: 'Community vote — Keep CuloTon tokens or rebrand? — CuloTon',
    metaDescription: 'Decide the future of the project: keep the current $CULO + $CTAX setup, or launch a new FOMO token and rebrand. Live community vote.',
    kicker: 'Community decision',
    h1: 'Where do we go next: keep or rebrand?',
    intro: [
      'We have two tokens live right now: $CULO (no tax) and $CTAX (with tax). The question on the table is whether to keep them as they are, or close that chapter and launch a single new, more FOMO-oriented token under a fresh brand.',
      'The culoton.fun portal will keep running exactly as it does today — news pipeline, AI desk, Telegram bot, everything. The vote is only about which token (or tokens) sit at the center of the project going forward. If "new token" wins, a rebrand follows.',
    ],
    noRefundNote: 'Heads up: if the community picks "new token", there will be no refund for existing $CULO / $CTAX holders. Almost no one but me holds anything today, so this is a practical call, not a financial one.',
    q1Label: 'Q1. Keep the current setup, or new FOMO token?',
    q1Keep: 'Keep both tokens as they are',
    q1KeepDesc: '$CULO (no tax) and $CTAX (with tax) stay live, no rebrand.',
    q1New: 'Launch a new FOMO token and rebrand',
    q1NewDesc: 'Fresh token, fresh ticker, new launch — portal keeps running.',
    q2Label: 'Q2. (If new token) — should it have a tax?',
    q2Tax: 'With tax',
    q2TaxDesc: 'Buy/sell tax on every trade, redistributed to holders + dev.',
    q2NoTax: 'No tax',
    q2NoTaxDesc: 'Pure trade, zero buy/sell fee.',
    buyLabel: 'Buy tax %',
    sellLabel: 'Sell tax %',
    splitLabel: 'Split holders / dev',
    splitOptions: {
      '100-0': '100% holders / 0% dev',
      '80-20': '80% / 20%',
      '60-40': '60% / 40%',
      '50-50': '50% / 50%',
      '40-60': '40% / 60%',
    },
    tickerLabel: 'Ticker suggestion (optional)',
    tickerHint: 'A-Z, 0-9, 2–12 chars. Example: FOMOTON',
    tickerPlaceholder: 'YOURTICKER',
    submit: 'Submit my vote',
    submitting: 'Submitting…',
    alreadyVoted: 'You have already voted from this network. Showing current results.',
    thanks: 'Thanks for voting. Here are the live results:',
    errorGeneric: 'Something went wrong submitting your vote. Try again in a moment.',
    resultsH: 'Live results',
    resultsBlurb: 'Updates automatically every 15 seconds.',
    resultsLoading: 'Loading results…',
    resultsTotal: (n) => `${n} vote${n === 1 ? '' : 's'} so far`,
    resultsEmpty: 'No votes yet — be the first.',
    resultsTickers: 'Top ticker suggestions',
    resultsTickersEmpty: 'No suggestions yet.',
    resultsTaxBreakdown: 'Tax % preferences (votes)',
    resultsSplitBreakdown: 'Holders / dev split (votes)',
    refreshAuto: 'Auto-refresh on',
  },
  pl: {
    pageTitle: 'Głosowanie społeczności — zostawić tokeny CuloTon czy rebranding? — CuloTon',
    metaDescription: 'Zdecyduj o przyszłości projektu: zostawić $CULO + $CTAX czy odpalić nowy token FOMO i przeprowadzić rebranding. Wyniki na żywo.',
    kicker: 'Decyzja społeczności',
    h1: 'Co dalej: zostawiamy czy rebranding?',
    intro: [
      'Mamy obecnie dwa tokeny: $CULO (bez tax) i $CTAX (z tax). Pytanie brzmi: zostawiamy je w obecnym kształcie, czy zamykamy ten rozdział i odpalamy jeden nowy, bardziej FOMO token pod świeżą marką?',
      'Portal culoton.fun działa dalej dokładnie tak jak dziś — pipeline newsów, redakcja AI, bot Telegram, wszystko. Głosowanie dotyczy tylko tego, który token (lub tokeny) stoją w centrum projektu. Jeśli wygra "nowy token" — będzie rebranding.',
    ],
    noRefundNote: 'Ważne: jeśli społeczność wybierze "nowy token", nie będzie refundu dla obecnych holderów $CULO / $CTAX. Praktycznie nikt poza mną dziś nic nie trzyma, więc to decyzja praktyczna, nie finansowa.',
    q1Label: 'P1. Zostawiamy obecny układ czy nowy token FOMO?',
    q1Keep: 'Zostawiamy oba tokeny jak są',
    q1KeepDesc: '$CULO (bez tax) i $CTAX (z tax) zostają na żywo, brak rebrandingu.',
    q1New: 'Odpalamy nowy token FOMO + rebranding',
    q1NewDesc: 'Nowy token, nowy ticker, nowy launch — portal działa dalej.',
    q2Label: 'P2. (Jeśli nowy token) — z tax czy bez?',
    q2Tax: 'Z tax',
    q2TaxDesc: 'Podatek od buy/sell, redystrybuowany do holderów + dev.',
    q2NoTax: 'Bez tax',
    q2NoTaxDesc: 'Czysty handel, zero opłat buy/sell.',
    buyLabel: 'Buy tax %',
    sellLabel: 'Sell tax %',
    splitLabel: 'Podział holderzy / dev',
    splitOptions: {
      '100-0': '100% holderzy / 0% dev',
      '80-20': '80% / 20%',
      '60-40': '60% / 40%',
      '50-50': '50% / 50%',
      '40-60': '40% / 60%',
    },
    tickerLabel: 'Propozycja tickera (opcjonalnie)',
    tickerHint: 'A-Z, 0-9, 2–12 znaków. Przykład: FOMOTON',
    tickerPlaceholder: 'TWOJTICKER',
    submit: 'Wyślij głos',
    submitting: 'Wysyłanie…',
    alreadyVoted: 'Z tej sieci już głosowałeś. Pokazuję aktualne wyniki.',
    thanks: 'Dzięki za głos. Aktualne wyniki na żywo:',
    errorGeneric: 'Coś poszło nie tak przy wysyłaniu głosu. Spróbuj za chwilę.',
    resultsH: 'Wyniki na żywo',
    resultsBlurb: 'Aktualizacja co 15 sekund.',
    resultsLoading: 'Ładowanie wyników…',
    resultsTotal: (n) => `Oddanych głosów: ${n}`,
    resultsEmpty: 'Brak głosów — bądź pierwszy.',
    resultsTickers: 'Top propozycje tickera',
    resultsTickersEmpty: 'Brak propozycji.',
    resultsTaxBreakdown: 'Preferencje tax % (głosy)',
    resultsSplitBreakdown: 'Podział holderzy / dev (głosy)',
    refreshAuto: 'Auto-odświeżanie włączone',
  },
  de: {
    pageTitle: 'Community-Abstimmung — CuloTon-Tokens behalten oder Rebrand? — CuloTon',
    metaDescription: 'Entscheide über die Zukunft des Projekts: $CULO + $CTAX behalten oder einen neuen FOMO-Token mit Rebrand starten. Live-Ergebnisse.',
    kicker: 'Community-Entscheidung',
    h1: 'Wie weiter: behalten oder Rebrand?',
    intro: [
      'Wir haben aktuell zwei Token: $CULO (ohne Tax) und $CTAX (mit Tax). Die Frage ist: lassen wir sie wie sie sind, oder schließen wir das Kapitel und starten einen einzigen neuen, stärker FOMO-getriebenen Token unter frischer Marke?',
      'Das Portal culoton.fun läuft genau wie heute weiter — News-Pipeline, AI-Redaktion, Telegram-Bot, alles. Die Abstimmung betrifft nur, welcher Token (oder welche Tokens) im Zentrum des Projekts stehen. Gewinnt „neuer Token", folgt ein Rebrand.',
    ],
    noRefundNote: 'Wichtig: Wenn die Community „neuer Token" wählt, gibt es keine Rückerstattung für bestehende $CULO- / $CTAX-Holder. Außer mir hält praktisch niemand etwas, also ist das eine praktische, keine finanzielle Entscheidung.',
    q1Label: 'F1. Aktuelles Setup behalten oder neuer FOMO-Token?',
    q1Keep: 'Beide Tokens unverändert behalten',
    q1KeepDesc: '$CULO (ohne Tax) und $CTAX (mit Tax) bleiben live, kein Rebrand.',
    q1New: 'Neuen FOMO-Token starten + Rebrand',
    q1NewDesc: 'Neuer Token, neuer Ticker, neuer Launch — Portal läuft weiter.',
    q2Label: 'F2. (Falls neuer Token) — mit oder ohne Tax?',
    q2Tax: 'Mit Tax',
    q2TaxDesc: 'Buy-/Sell-Steuer auf jeden Trade, verteilt an Holder + Dev.',
    q2NoTax: 'Ohne Tax',
    q2NoTaxDesc: 'Sauberer Handel, keine Buy-/Sell-Gebühr.',
    buyLabel: 'Buy-Tax %',
    sellLabel: 'Sell-Tax %',
    splitLabel: 'Aufteilung Holder / Dev',
    splitOptions: {
      '100-0': '100% Holder / 0% Dev',
      '80-20': '80% / 20%',
      '60-40': '60% / 40%',
      '50-50': '50% / 50%',
      '40-60': '40% / 60%',
    },
    tickerLabel: 'Ticker-Vorschlag (optional)',
    tickerHint: 'A-Z, 0-9, 2–12 Zeichen. Beispiel: FOMOTON',
    tickerPlaceholder: 'DEINTICKER',
    submit: 'Stimme abgeben',
    submitting: 'Wird gesendet…',
    alreadyVoted: 'Aus diesem Netzwerk wurde bereits abgestimmt. Zeige aktuelle Ergebnisse.',
    thanks: 'Danke für deine Stimme. Aktuelle Live-Ergebnisse:',
    errorGeneric: 'Beim Senden ist etwas schiefgelaufen. Bitte gleich erneut versuchen.',
    resultsH: 'Live-Ergebnisse',
    resultsBlurb: 'Aktualisierung alle 15 Sekunden.',
    resultsLoading: 'Ergebnisse werden geladen…',
    resultsTotal: (n) => `Bisher ${n} Stimme${n === 1 ? '' : 'n'}`,
    resultsEmpty: 'Noch keine Stimmen — sei die erste.',
    resultsTickers: 'Top Ticker-Vorschläge',
    resultsTickersEmpty: 'Noch keine Vorschläge.',
    resultsTaxBreakdown: 'Tax-% Präferenzen (Stimmen)',
    resultsSplitBreakdown: 'Holder- / Dev-Aufteilung (Stimmen)',
    refreshAuto: 'Auto-Aktualisierung an',
  },
};

export const TAX_BUCKETS = [0, 3, 5, 8, 10, 15] as const;
export const SPLIT_BUCKETS = ['100-0', '80-20', '60-40', '50-50', '40-60'] as const;

// RU/ES/UK fall back to EN content — main supported locales are EN/PL/DE per spec.
(POLL_STRINGS as Record<string, PollStrings>).ru = POLL_STRINGS.en;
(POLL_STRINGS as Record<string, PollStrings>).es = POLL_STRINGS.en;
(POLL_STRINGS as Record<string, PollStrings>).uk = POLL_STRINGS.en;
