// BRAINROT Launcher — jetton deploy engine.
//
// The smart-contract code below is the audited TEP-74 reference Jetton Master +
// Jetton Wallet, lifted VERBATIM from @ton-community/assets-sdk@0.0.5
// (ton-community / GRAM Foundation). We do not modify a byte — we only build the
// StateInit + mint message that the user's wallet signs via TonConnect.
//
// Message layout mirrors the SDK exactly:
//   mint:              op=21,          query_id, to, wallet_forward_value, ref(internal_transfer)
//   internal_transfer: op=0x178d4519,  query_id, amount, from, response_addr, fwd_ton, maybe_ref(payload)
//
// Metadata is on-chain (TEP-64): a dict keyed by sha256(field) → ref(0x00 snake string).
// No backend, no IPFS — the logo is referenced by URL.

import {
  Address,
  beginCell,
  Cell,
  contractAddress,
  Dictionary,
  toNano,
  storeStateInit,
  type DictionaryValue,
} from '@ton/core';
import { sha256_sync } from '@ton/crypto';

export const JETTON_MINTER_CODE_BOC =
  'te6ccgECDgEAAqMAART/APSkE/S88sgLAQIBYgIDAgLMBAUCA3pgDA0B9dkGOASS+B8ADoaYGAuNhJL4HwfSB9IBj9ABi465D9ABj9ABg51NoAAWmP6Z/2omh9AH0gamoYQAqpOF1HGZqamxsommOC+XAkgX0gfQBqGBBoQDBrkP0AGBKIGigheASKUCgZ5CgCfQEsZ4tmZmT2qnBBCD3uy+8pOF1AYAk7PwUIgG4KhAJqgoB5CgCfQEsZ4sA54tmZJFkZYCJegB6AGWAZJB8gDg6ZGWBZQPl/+ToO8AMZGWCrGeLKAJ9AQnltYlmZmS4/YBBPSO4DY3NwH6APpA+ChUEgZwVCATVBQDyFAE+gJYzxYBzxbMySLIywES9AD0AMsAyfkAcHTIywLKB8v/ydBQBscF8uBKoQNFRchQBPoCWM8WzMzJ7VQB+kAwINcLAcMAkVvjDeCCECx2uXNScLrjAjU3NyPAA+MCNQLABAcICQoAPoIQ1TJ223CAEMjLBVADzxYi+gISy2rLH8s/yYBC+wAB/jZfA4IImJaAFaAVvPLgSwL6QNMAMJXIIc8WyZFt4oIQ0XNUAHCAGMjLBVAFzxYk+gIUy2oTyx8Uyz8j+kQwcLqOM/goRANwVCATVBQDyFAE+gJYzxYBzxbMySLIywES9AD0AMsAyfkAcHTIywLKB8v/ydDPFpZsInABywHi9AALADQzUDXHBfLgSQP6QDBZyFAE+gJYzxbMzMntVABCjhhRJMcF8uBJ1DBDAMhQBPoCWM8WzMzJ7VTgXwWED/LwAArJgED7AAB9rbz2omh9AH0gamoYNhj8FAC4KhAJqgoB5CgCfQEsZ4sA54tmZJFkZYCJegB6AGWAZPyAODpkZYFlA+X/5OhAAB+vFvaiaH0AfSBqahg/qpBA';

export const JETTON_WALLET_CODE_BOC =
  'te6ccgECEgEAAzQAART/APSkE/S88sgLAQIBYgIDAgLMBAUAG6D2BdqJofQB9IH0gahhAgHUBgcCAUgICQDDCDHAJJfBOAB0NMDAXGwlRNfA/AL4PpA+kAx+gAxcdch+gAx+gAwc6m0AALTH4IQD4p+pVIgupUxNFnwCOCCEBeNRRlSILqWMUREA/AJ4DWCEFlfB7y6k1nwCuBfBIQP8vCAAET6RDBwuvLhTYAIBIAoLAgEgEBEB8QD0z/6APpAIfAB7UTQ+gD6QPpA1DBRNqFSKscF8uLBKML/8uLCVDRCcFQgE1QUA8hQBPoCWM8WAc8WzMkiyMsBEvQA9ADLAMkg+QBwdMjLAsoHy//J0AT6QPQEMfoAINdJwgDy4sR3gBjIywVQCM8WcPoCF8trE8yAMA/c7UTQ+gD6QPpA1DAI0z/6AFFRoAX6QPpAU1vHBVRzbXBUIBNUFAPIUAT6AljPFgHPFszJIsjLARL0APQAywDJ+QBwdMjLAsoHy//J0FANxwUcsfLiwwr6AFGooYIImJaAggiYloAStgihggjk4cCgGKEn4w8l1wsBwwAjgDQ4PAK6CEBeNRRnIyx8Zyz9QB/oCIs8WUAbPFiX6AlADzxbJUAXMI5FykXHiUAioE6CCCOThwKoAggiYloCgoBS88uLFBMmAQPsAECPIUAT6AljPFgHPFszJ7VQAcFJ5oBihghBzYtCcyMsfUjDLP1j6AlAHzxZQB88WyXGAEMjLBSTPFlAG+gIVy2oUzMlx+wAQJBAjAA4QSRA4N18EAHbCALCOIYIQ1TJ223CAEMjLBVAIzxZQBPoCFstqEssfEss/yXL7AJM1bCHiA8hQBPoCWM8WAc8WzMntVADbO1E0PoA+kD6QNQwB9M/+gD6QDBRUaFSSccF8uLBJ8L/8uLCggjk4cCqABagFrzy4sOCEHvdl97Iyx8Vyz9QA/oCIs8WAc8WyXGAGMjLBSTPFnD6AstqzMmAQPsAQBPIUAT6AljPFgHPFszJ7VSAAgyAINch7UTQ+gD6QPpA1DAE0x+CEBeNRRlSILqCEHvdl94TuhKx8uLF0z8x+gAwE6BQI8hQBPoCWM8WAc8WzMntVIA==';

const MINT_OP = 21;
const INTERNAL_TRANSFER_OP = 0x178d4519;
const CHANGE_ADMIN_OP = 3;

// GRAM forwarded to the freshly-minted jetton wallet (covers its deploy + storage).
const WALLET_FORWARD = toNano('0.05');
// Total GRAM attached to the deploy+mint message. Excess returns to the owner.
export const DEPLOY_AMOUNT = toNano('0.2');
export const RENOUNCE_AMOUNT = toNano('0.05');

function snakeCell(s: string): Cell {
  return beginCell().storeUint(0, 8).storeStringTail(s).endCell();
}

const SnakeValue: DictionaryValue<string> = {
  serialize: (src, builder) => {
    builder.storeRef(snakeCell(src));
  },
  parse: (src) => {
    const r = src.loadRef().beginParse();
    r.loadUint(8);
    return r.loadStringTail();
  },
};

function contentKey(k: string): bigint {
  return BigInt('0x' + sha256_sync(k).toString('hex'));
}

export interface JettonParams {
  /** Admin + recipient of the minted supply. */
  owner: Address;
  name: string;
  symbol: string;
  decimals: number;
  description?: string;
  /** Logo URL (https or ipfs://). Stored on-chain as TEP-64 "image". */
  image?: string;
  /** Whole-token supply (before applying decimals). */
  supply: bigint;
}

/** TEP-64 on-chain metadata cell. */
export function buildOnchainContent(p: JettonParams): Cell {
  const dict = Dictionary.empty(Dictionary.Keys.BigUint(256), SnakeValue);
  dict.set(contentKey('name'), p.name);
  dict.set(contentKey('symbol'), p.symbol);
  dict.set(contentKey('decimals'), String(p.decimals));
  if (p.description) dict.set(contentKey('description'), p.description);
  if (p.image) dict.set(contentKey('image'), p.image);
  return beginCell().storeUint(0, 8).storeDict(dict).endCell();
}

export function jettonMinterStateInit(p: JettonParams) {
  const code = Cell.fromBase64(JETTON_MINTER_CODE_BOC);
  const walletCode = Cell.fromBase64(JETTON_WALLET_CODE_BOC);
  const content = buildOnchainContent(p);
  const data = beginCell()
    .storeCoins(0) // total_supply starts at 0; mint raises it
    .storeAddress(p.owner) // admin
    .storeRef(content)
    .storeRef(walletCode)
    .endCell();
  const init = { code, data };
  return { init, address: contractAddress(0, init) };
}

export function buildMintBody(minter: Address, owner: Address, jettonUnits: bigint): Cell {
  const internalTransfer = beginCell()
    .storeUint(INTERNAL_TRANSFER_OP, 32)
    .storeUint(0, 64)
    .storeCoins(jettonUnits)
    .storeAddress(minter) // from
    .storeAddress(owner) // response (excess back to deployer)
    .storeCoins(0) // forward_ton_amount
    .storeMaybeRef(null)
    .endCell();
  return beginCell()
    .storeUint(MINT_OP, 32)
    .storeUint(0, 64)
    .storeAddress(owner) // recipient
    .storeCoins(WALLET_FORWARD)
    .storeRef(internalTransfer)
    .endCell();
}

export interface DeployTx {
  minterAddress: Address;
  amount: bigint;
  stateInitB64: string;
  payloadB64: string;
}

/** Build the single deploy+mint transaction for TonConnect. */
export function buildDeployTx(p: JettonParams): DeployTx {
  const { init, address } = jettonMinterStateInit(p);
  const jettonUnits = p.supply * 10n ** BigInt(p.decimals);
  const stateInit = beginCell().store(storeStateInit(init)).endCell();
  const payload = buildMintBody(address, p.owner, jettonUnits);
  return {
    minterAddress: address,
    amount: DEPLOY_AMOUNT,
    stateInitB64: stateInit.toBoc().toString('base64'),
    payloadB64: payload.toBoc().toString('base64'),
  };
}

/** Set admin to addr_none — renounces mint/metadata control forever. */
export function buildRenounceBody(): Cell {
  return beginCell()
    .storeUint(CHANGE_ADMIN_OP, 32)
    .storeUint(0, 64)
    .storeAddress(null) // addr_none
    .endCell();
}
