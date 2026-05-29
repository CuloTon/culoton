// BRAINROT Launcher — client wiring. Runs only on /launch.
// @ton/* need a Buffer global in the browser, so we set it BEFORE any dynamic
// import that pulls them in.
import { Buffer } from 'buffer';
(globalThis as any).Buffer = (globalThis as any).Buffer || Buffer;
(globalThis as any).global = (globalThis as any).global || globalThis;

const TESTNET = '-3'; // CHAIN.TESTNET

// Localized status/confirm strings, keyed by <html lang>. Falls back to en.
type Msgs = {
  mainnet: string; connected: string; connectFirst: string; nameSymbol: string;
  decimals: string; supplyInt: string; supplyPos: string; logoUrl: string;
  confirmTx: string; signed: string; deployFail: string; renounceConfirm: string;
  renounceConfirmTx: string; renounceSigned: string; renounceSubmitted: string;
  renounceFail: string; disconnect: string; connect: string; loadFail: string;
};
const I18N: Record<string, Msgs> = {
  en: {
    mainnet: 'Wallet is on MAINNET — switch it to TESTNET, or the deploy will be rejected.',
    connected: 'Testnet wallet connected. Fill the form and deploy.',
    connectFirst: 'Connect a wallet first.',
    nameSymbol: 'Name and symbol are required.',
    decimals: 'Decimals must be a whole number between 0 and 30 (use 9).',
    supplyInt: 'Total supply must be a whole number.',
    supplyPos: 'Total supply must be greater than zero.',
    logoUrl: 'Logo must be an http(s):// or ipfs:// URL.',
    confirmTx: 'Confirm the transaction in your wallet…',
    signed: 'Signed! Your jetton is deploying — it appears on-chain in ~10 seconds.',
    deployFail: 'Deploy cancelled or failed: ',
    renounceConfirm: 'Renounce admin permanently? Nobody — including you — will be able to mint, edit metadata, or change admin again.',
    renounceConfirmTx: 'Confirm the renounce transaction in your wallet…',
    renounceSigned: 'Renounce signed. Admin will be set to none on-chain shortly.',
    renounceSubmitted: 'Renounce submitted ✓',
    renounceFail: 'Renounce cancelled or failed: ',
    disconnect: 'Disconnect ', connect: 'Connect TON wallet (testnet)',
    loadFail: 'Launcher failed to load: ',
  },
  pl: {
    mainnet: 'Portfel jest na MAINNECIE — przełącz na TESTNET, inaczej deploy zostanie odrzucony.',
    connected: 'Portfel testnet podłączony. Wypełnij formularz i wdróż.',
    connectFirst: 'Najpierw podłącz portfel.',
    nameSymbol: 'Nazwa i symbol są wymagane.',
    decimals: 'Miejsca dziesiętne muszą być liczbą całkowitą 0–30 (użyj 9).',
    supplyInt: 'Całkowita podaż musi być liczbą całkowitą.',
    supplyPos: 'Całkowita podaż musi być większa od zera.',
    logoUrl: 'Logo musi być adresem http(s):// lub ipfs://.',
    confirmTx: 'Potwierdź transakcję w portfelu…',
    signed: 'Podpisano! Twój jetton się wdraża — pojawi się on-chain za ~10 sekund.',
    deployFail: 'Deploy anulowany lub nieudany: ',
    renounceConfirm: 'Zrzec się admina na stałe? Nikt — łącznie z Tobą — nie będzie już mógł mintować, zmieniać metadanych ani admina.',
    renounceConfirmTx: 'Potwierdź transakcję zrzeczenia w portfelu…',
    renounceSigned: 'Zrzeczenie podpisane. Admin zostanie wkrótce ustawiony na zerowy on-chain.',
    renounceSubmitted: 'Zrzeczenie wysłane ✓',
    renounceFail: 'Zrzeczenie anulowane lub nieudane: ',
    disconnect: 'Rozłącz ', connect: 'Podłącz portfel TON (testnet)',
    loadFail: 'Nie udało się załadować launchera: ',
  },
  ru: {
    mainnet: 'Кошелёк в MAINNET — переключи на TESTNET, иначе деплой отклонят.',
    connected: 'Тестнет-кошелёк подключён. Заполни форму и разверни.',
    connectFirst: 'Сначала подключи кошелёк.',
    nameSymbol: 'Название и символ обязательны.',
    decimals: 'Десятичные должны быть целым числом от 0 до 30 (ставь 9).',
    supplyInt: 'Общая эмиссия должна быть целым числом.',
    supplyPos: 'Общая эмиссия должна быть больше нуля.',
    logoUrl: 'Логотип должен быть URL вида http(s):// или ipfs://.',
    confirmTx: 'Подтверди транзакцию в кошельке…',
    signed: 'Подписано! Твой джеттон разворачивается — появится on-chain через ~10 секунд.',
    deployFail: 'Деплой отменён или не удался: ',
    renounceConfirm: 'Отказаться от админки навсегда? Никто — включая тебя — больше не сможет минтить, менять метаданные или админа.',
    renounceConfirmTx: 'Подтверди транзакцию отказа в кошельке…',
    renounceSigned: 'Отказ подписан. Админ скоро будет обнулён on-chain.',
    renounceSubmitted: 'Отказ отправлен ✓',
    renounceFail: 'Отказ отменён или не удался: ',
    disconnect: 'Отключить ', connect: 'Подключить кошелёк TON (тестнет)',
    loadFail: 'Не удалось загрузить лаунчер: ',
  },
  de: {
    mainnet: 'Wallet ist im MAINNET — wechsle ins TESTNET, sonst wird der Deploy abgelehnt.',
    connected: 'Testnet-Wallet verbunden. Formular ausfüllen und deployen.',
    connectFirst: 'Zuerst eine Wallet verbinden.',
    nameSymbol: 'Name und Symbol sind erforderlich.',
    decimals: 'Dezimalstellen müssen eine ganze Zahl zwischen 0 und 30 sein (nimm 9).',
    supplyInt: 'Der Gesamtsupply muss eine ganze Zahl sein.',
    supplyPos: 'Der Gesamtsupply muss größer als null sein.',
    logoUrl: 'Das Logo muss eine http(s)://- oder ipfs://-URL sein.',
    confirmTx: 'Bestätige die Transaktion in deiner Wallet…',
    signed: 'Signiert! Dein Jetton wird deployt — es erscheint in ~10 Sekunden on-chain.',
    deployFail: 'Deploy abgebrochen oder fehlgeschlagen: ',
    renounceConfirm: 'Admin dauerhaft abgeben? Niemand — auch du nicht — kann dann je wieder minten, Metadaten ändern oder den Admin wechseln.',
    renounceConfirmTx: 'Bestätige die Abgabe-Transaktion in deiner Wallet…',
    renounceSigned: 'Abgabe signiert. Admin wird in Kürze on-chain auf null gesetzt.',
    renounceSubmitted: 'Abgabe eingereicht ✓',
    renounceFail: 'Abgabe abgebrochen oder fehlgeschlagen: ',
    disconnect: 'Trennen ', connect: 'TON-Wallet verbinden (Testnet)',
    loadFail: 'Launcher konnte nicht geladen werden: ',
  },
  es: {
    mainnet: 'La wallet está en MAINNET — cámbiala a TESTNET o se rechazará el despliegue.',
    connected: 'Wallet de testnet conectada. Rellena el formulario y despliega.',
    connectFirst: 'Conecta una wallet primero.',
    nameSymbol: 'El nombre y el símbolo son obligatorios.',
    decimals: 'Los decimales deben ser un número entero entre 0 y 30 (usa 9).',
    supplyInt: 'El supply total debe ser un número entero.',
    supplyPos: 'El supply total debe ser mayor que cero.',
    logoUrl: 'El logo debe ser una URL http(s):// o ipfs://.',
    confirmTx: 'Confirma la transacción en tu wallet…',
    signed: '¡Firmado! Tu jetton se está desplegando — aparece on-chain en ~10 segundos.',
    deployFail: 'Despliegue cancelado o fallido: ',
    renounceConfirm: '¿Renunciar al admin para siempre? Nadie — ni tú — podrá volver a mintear, editar metadatos o cambiar el admin.',
    renounceConfirmTx: 'Confirma la transacción de renuncia en tu wallet…',
    renounceSigned: 'Renuncia firmada. El admin se pondrá a nulo on-chain en breve.',
    renounceSubmitted: 'Renuncia enviada ✓',
    renounceFail: 'Renuncia cancelada o fallida: ',
    disconnect: 'Desconectar ', connect: 'Conectar wallet TON (testnet)',
    loadFail: 'No se pudo cargar el launcher: ',
  },
  uk: {
    mainnet: 'Гаманець у MAINNET — переключи на TESTNET, інакше деплой відхилять.',
    connected: 'Тестнет-гаманець підключено. Заповни форму та розгорни.',
    connectFirst: 'Спершу підключи гаманець.',
    nameSymbol: 'Назва та символ обовʼязкові.',
    decimals: 'Десяткові мають бути цілим числом від 0 до 30 (став 9).',
    supplyInt: 'Загальна емісія має бути цілим числом.',
    supplyPos: 'Загальна емісія має бути більшою за нуль.',
    logoUrl: 'Логотип має бути URL виду http(s):// або ipfs://.',
    confirmTx: 'Підтверди транзакцію в гаманці…',
    signed: 'Підписано! Твій джетон розгортається — зʼявиться on-chain за ~10 секунд.',
    deployFail: 'Деплой скасовано або не вдався: ',
    renounceConfirm: 'Відмовитися від адмінки назавжди? Ніхто — включно з тобою — більше не зможе мінтити, змінювати метадані чи адміна.',
    renounceConfirmTx: 'Підтверди транзакцію відмови в гаманці…',
    renounceSigned: 'Відмову підписано. Адміна невдовзі буде обнулено on-chain.',
    renounceSubmitted: 'Відмову надіслано ✓',
    renounceFail: 'Відмову скасовано або не вдалася: ',
    disconnect: 'Відключити ', connect: 'Підключити гаманець TON (тестнет)',
    loadFail: 'Не вдалося завантажити лаунчер: ',
  },
};
const LANG = (document.documentElement.lang || 'en').slice(0, 2);
const M: Msgs = I18N[LANG] || I18N.en;

function $(id: string): HTMLElement | null {
  return document.getElementById(id);
}

async function main() {
  const form = $('jl-form') as HTMLFormElement | null;
  if (!form) return; // not on the launcher page

  const [{ Address }, jetton, tc] = await Promise.all([
    import('@ton/core'),
    import('../lib/jetton'),
    import('@tonconnect/ui'),
  ]);

  const statusEl = $('jl-status')!;
  const connectBtn = $('jl-connect') as HTMLButtonElement;
  const deployBtn = $('jl-deploy') as HTMLButtonElement;
  const resultEl = $('jl-result')!;
  const addrEl = $('jl-address')!;
  const explorerEl = $('jl-explorer') as HTMLAnchorElement;
  const renounceBtn = $('jl-renounce') as HTMLButtonElement;

  const tcui = new tc.TonConnectUI({
    manifestUrl: new URL('/tonconnect-manifest.json', location.origin).href,
  });

  let lastMinter: string | null = null;

  function setStatus(msg: string, kind: 'info' | 'error' | 'ok' = 'info') {
    statusEl.textContent = msg;
    statusEl.dataset.kind = kind;
  }

  function refreshConnection() {
    const acc = tcui.account;
    if (acc) {
      const short = acc.address.slice(0, 6) + '…' + acc.address.slice(-4);
      connectBtn.textContent = M.disconnect + short;
      connectBtn.dataset.connected = 'true';
      deployBtn.disabled = false;
      if (acc.chain && acc.chain !== TESTNET) {
        setStatus(M.mainnet, 'error');
      } else {
        setStatus(M.connected, 'ok');
      }
    } else {
      connectBtn.textContent = M.connect;
      connectBtn.dataset.connected = 'false';
      deployBtn.disabled = true;
    }
  }

  tcui.onStatusChange(() => refreshConnection());
  refreshConnection();

  connectBtn.addEventListener('click', async () => {
    if (tcui.account) {
      await tcui.disconnect();
    } else {
      await tcui.openModal();
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!tcui.account) {
      setStatus(M.connectFirst, 'error');
      return;
    }

    const name = (($('jl-name') as HTMLInputElement).value || '').trim();
    const symbol = (($('jl-symbol') as HTMLInputElement).value || '').trim();
    const decimals = parseInt(($('jl-decimals') as HTMLInputElement).value, 10);
    const supplyStr = (($('jl-supply') as HTMLInputElement).value || '').trim();
    const description = (($('jl-desc') as HTMLTextAreaElement).value || '').trim();
    const image = (($('jl-image') as HTMLInputElement).value || '').trim();

    if (!name || !symbol) {
      setStatus(M.nameSymbol, 'error');
      return;
    }
    if (!Number.isInteger(decimals) || decimals < 0 || decimals > 30) {
      setStatus(M.decimals, 'error');
      return;
    }
    let supply: bigint;
    try {
      supply = BigInt(supplyStr.replace(/[\s,_]/g, ''));
    } catch {
      setStatus(M.supplyInt, 'error');
      return;
    }
    if (supply <= 0n) {
      setStatus(M.supplyPos, 'error');
      return;
    }
    if (image && !/^https?:\/\/|^ipfs:\/\//.test(image)) {
      setStatus(M.logoUrl, 'error');
      return;
    }

    try {
      const owner = Address.parse(tcui.account.address);
      const tx = jetton.buildDeployTx({ owner, name, symbol, decimals, description, image, supply });

      const minterMsgAddr = tx.minterAddress.toString({ bounceable: false, testOnly: true });
      const minterDisplay = tx.minterAddress.toString({ bounceable: true, testOnly: true });
      lastMinter = minterMsgAddr;

      deployBtn.disabled = true;
      setStatus(M.confirmTx, 'info');

      await tcui.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 600,
        network: TESTNET,
        messages: [
          {
            address: minterMsgAddr,
            amount: tx.amount.toString(),
            stateInit: tx.stateInitB64,
            payload: tx.payloadB64,
          },
        ],
      });

      addrEl.textContent = minterDisplay;
      explorerEl.href = 'https://testnet.tonviewer.com/' + minterDisplay;
      resultEl.hidden = false;
      resultEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setStatus(M.signed, 'ok');
    } catch (err: any) {
      setStatus(M.deployFail + (err?.message || String(err)), 'error');
    } finally {
      deployBtn.disabled = !tcui.account;
    }
  });

  renounceBtn.addEventListener('click', async () => {
    if (!tcui.account || !lastMinter) return;
    if (!confirm(M.renounceConfirm)) {
      return;
    }
    try {
      renounceBtn.disabled = true;
      setStatus(M.renounceConfirmTx, 'info');
      const body = jetton.buildRenounceBody();
      await tcui.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 600,
        network: TESTNET,
        messages: [
          {
            address: lastMinter,
            amount: jetton.RENOUNCE_AMOUNT.toString(),
            payload: body.toBoc().toString('base64'),
          },
        ],
      });
      setStatus(M.renounceSigned, 'ok');
      renounceBtn.textContent = M.renounceSubmitted;
    } catch (err: any) {
      renounceBtn.disabled = false;
      setStatus(M.renounceFail + (err?.message || String(err)), 'error');
    }
  });
}

main().catch((e) => {
  const s = document.getElementById('jl-status');
  if (s) s.textContent = (I18N[(document.documentElement.lang || 'en').slice(0, 2)] || I18N.en).loadFail + (e?.message || String(e));
});
