// BRAINROT Launcher — client wiring. Runs only on /launch.
// @ton/* need a Buffer global in the browser, so we set it BEFORE any dynamic
// import that pulls them in.
import { Buffer } from 'buffer';
(globalThis as any).Buffer = (globalThis as any).Buffer || Buffer;
(globalThis as any).global = (globalThis as any).global || globalThis;

const TESTNET = '-3'; // CHAIN.TESTNET

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
      connectBtn.textContent = 'Disconnect ' + short;
      connectBtn.dataset.connected = 'true';
      deployBtn.disabled = false;
      if (acc.chain && acc.chain !== TESTNET) {
        setStatus('Wallet is on MAINNET — switch it to TESTNET, or the deploy will be rejected.', 'error');
      } else {
        setStatus('Testnet wallet connected. Fill the form and deploy.', 'ok');
      }
    } else {
      connectBtn.textContent = 'Connect TON wallet (testnet)';
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
      setStatus('Connect a wallet first.', 'error');
      return;
    }

    const name = (($('jl-name') as HTMLInputElement).value || '').trim();
    const symbol = (($('jl-symbol') as HTMLInputElement).value || '').trim();
    const decimals = parseInt(($('jl-decimals') as HTMLInputElement).value, 10);
    const supplyStr = (($('jl-supply') as HTMLInputElement).value || '').trim();
    const description = (($('jl-desc') as HTMLTextAreaElement).value || '').trim();
    const image = (($('jl-image') as HTMLInputElement).value || '').trim();

    if (!name || !symbol) {
      setStatus('Name and symbol are required.', 'error');
      return;
    }
    if (!Number.isInteger(decimals) || decimals < 0 || decimals > 30) {
      setStatus('Decimals must be a whole number between 0 and 30 (use 9).', 'error');
      return;
    }
    let supply: bigint;
    try {
      supply = BigInt(supplyStr.replace(/[\s,_]/g, ''));
    } catch {
      setStatus('Total supply must be a whole number.', 'error');
      return;
    }
    if (supply <= 0n) {
      setStatus('Total supply must be greater than zero.', 'error');
      return;
    }
    if (image && !/^https?:\/\/|^ipfs:\/\//.test(image)) {
      setStatus('Logo must be an http(s):// or ipfs:// URL.', 'error');
      return;
    }

    try {
      const owner = Address.parse(tcui.account.address);
      const tx = jetton.buildDeployTx({ owner, name, symbol, decimals, description, image, supply });

      const minterMsgAddr = tx.minterAddress.toString({ bounceable: false, testOnly: true });
      const minterDisplay = tx.minterAddress.toString({ bounceable: true, testOnly: true });
      lastMinter = minterMsgAddr;

      deployBtn.disabled = true;
      setStatus('Confirm the transaction in your wallet…', 'info');

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
      setStatus('Signed! Your jetton is deploying — it appears on-chain in ~10 seconds.', 'ok');
    } catch (err: any) {
      setStatus('Deploy cancelled or failed: ' + (err?.message || String(err)), 'error');
    } finally {
      deployBtn.disabled = !tcui.account;
    }
  });

  renounceBtn.addEventListener('click', async () => {
    if (!tcui.account || !lastMinter) return;
    if (!confirm('Renounce admin permanently? Nobody — including you — will be able to mint, edit metadata, or change admin again.')) {
      return;
    }
    try {
      renounceBtn.disabled = true;
      setStatus('Confirm the renounce transaction in your wallet…', 'info');
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
      setStatus('Renounce signed. Admin will be set to none on-chain shortly.', 'ok');
      renounceBtn.textContent = 'Renounce submitted ✓';
    } catch (err: any) {
      renounceBtn.disabled = false;
      setStatus('Renounce cancelled or failed: ' + (err?.message || String(err)), 'error');
    }
  });
}

main().catch((e) => {
  const s = document.getElementById('jl-status');
  if (s) s.textContent = 'Launcher failed to load: ' + (e?.message || String(e));
});
