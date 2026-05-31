"""BRAINROT $BRT rewards snapshot — READ-ONLY, no keys, no sending.

Computes the payout PLAN for a reward round:
  pool      = REWARD_PCT (25%) of the DEV wallet TON balance right now
  per holder= pool * (holder_BRT / total_eligible_BRT)

Rules (mirrored by rewards_payout.py):
  * A round only runs when the DEV balance >= MIN_BANK_TON (4 TON -> pool >= 1 TON).
  * Holders whose share < MIN_PAYOUT_TON are skipped — their share rolls over
    (dust would cost more in gas than it's worth).
  * Gas (~GAS_PER_TX each) is paid by the project; holders get their full share.

Excluded from the holder set: the DEV wallet, the jetton master, the burn
address, and any holder that is a contract rather than a plain wallet (this
removes the DeDust LP pool and other non-EOA holders).

Run:  python scripts/rewards_snapshot.py
Reads public chain data via tonapi. Nothing is signed or sent.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

DEV_ADDRESS = "UQBzaZXIwj3mDY8HdYDkTO1lkn4OV8sfx2tsf-lChQex70NP"
BRT_MASTER = "EQDsbT3_IfYbdN4hgDCFK8-AGQ7x0FpVspYPEN8sDpkm2PIh"

REWARD_PCT = 0.25          # 25% of the DEV balance forms the pool
MIN_BANK_TON = 4.0         # a round only runs when DEV balance >= this (pool >= 1 TON)
MIN_PAYOUT_TON = 0.05      # skip holders whose share is below this
GAS_PER_TX = 0.006         # rough network gas per transfer (project-paid)
NANO = 1_000_000_000

TONAPI = "https://tonapi.io/v2"
ROOT = Path(__file__).resolve().parent.parent
BURN = "0:0000000000000000000000000000000000000000000000000000000000000000"


def api_get(path: str) -> dict:
    url = f"{TONAPI}{path}"
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429:
                time.sleep(1.5 * (attempt + 1)); continue
            raise
        except Exception as e:
            last = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"tonapi failed: {url} ({last})")


def is_plain_wallet(address: str) -> bool:
    """True if the account is an ordinary wallet (EOA), not a contract/pool."""
    try:
        info = api_get(f"/accounts/{address}")
    except Exception:
        return False
    ifaces = info.get("interfaces") or []
    return any("wallet" in str(i).lower() for i in ifaces)


def build_plan() -> dict:
    """Compute the full reward plan from live chain data. No keys, read-only."""
    dev = api_get(f"/accounts/{DEV_ADDRESS}")
    dev_raw = dev.get("address", "")
    dev_balance_ton = int(dev.get("balance", 0)) / NANO
    pool_ton = round(dev_balance_ton * REWARD_PCT, 9)
    gate_open = dev_balance_ton >= MIN_BANK_TON

    master = api_get(f"/accounts/{BRT_MASTER}")
    master_raw = master.get("address", "")

    holders_resp = api_get(f"/jettons/{BRT_MASTER}/holders?limit=1000")
    raw_holders = holders_resp.get("addresses", [])

    excluded, eligible = [], []
    for h in raw_holders:
        addr = (h.get("owner") or {}).get("address", "")
        bal = int(h.get("balance", 0))
        if bal <= 0 or not addr:
            continue
        low = addr.lower()
        if low == dev_raw.lower():
            excluded.append((addr, bal, "DEV wallet")); continue
        if low == master_raw.lower():
            excluded.append((addr, bal, "jetton master")); continue
        if addr == BURN:
            excluded.append((addr, bal, "burn")); continue
        time.sleep(0.2)
        if not is_plain_wallet(addr):
            excluded.append((addr, bal, "contract / LP pool")); continue
        eligible.append((addr, bal))

    total_elig = sum(b for _, b in eligible)
    paid, skipped = [], []
    if total_elig > 0:
        for addr, bal in eligible:
            share = round(pool_ton * bal / total_elig, 9)
            (paid if share >= MIN_PAYOUT_TON else skipped).append((addr, bal, share))
    paid.sort(key=lambda x: x[2], reverse=True)
    skipped.sort(key=lambda x: x[2], reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dev_address": DEV_ADDRESS, "brt_master": BRT_MASTER,
        "reward_pct": REWARD_PCT, "min_bank_ton": MIN_BANK_TON, "min_payout_ton": MIN_PAYOUT_TON,
        "dev_balance_ton": dev_balance_ton, "pool_ton": pool_ton, "gate_open": gate_open,
        "total_eligible_brt": total_elig,
        "paid": [{"address": a, "brt": b, "ton": s} for a, b, s in paid],
        "skipped": [{"address": a, "brt": b, "ton": s} for a, b, s in skipped],
        "excluded": [{"address": a, "brt": b, "reason": w} for a, b, w in excluded],
        "total_paid_ton": round(sum(s for _, _, s in paid), 9),
        "gas_estimate_ton": round(len(paid) * GAS_PER_TX, 9),
    }


def _short(a: str) -> str:
    return a[:10] + "…" + a[-6:] if len(a) > 18 else a


def print_plan(p: dict) -> None:
    print(f"BRAINROT rewards snapshot  ({p['generated_at']})")
    print("-" * 64)
    print(f"DEV wallet balance : {p['dev_balance_ton']:.4f} TON")
    print(f"Pool (25%)         : {p['pool_ton']:.4f} TON")
    if p["gate_open"]:
        print(f"Payout gate        : OPEN (bank >= {p['min_bank_ton']} TON)")
    else:
        need = round(p["min_bank_ton"] - p["dev_balance_ton"], 4)
        print(f"Payout gate        : HOLDING — bank below {p['min_bank_ton']} TON "
              f"(need +{need} TON). Projection only; no round runs yet.")

    if p["excluded"]:
        print("\nExclusions:")
        for e in p["excluded"]:
            print(f"  - {_short(e['address'])}  {e['brt']/NANO:>14.2f} BRT   [{e['reason']}]")

    total_elig_wallets = len(p["paid"]) + len(p["skipped"])
    print(f"\nEligible wallets   : {total_elig_wallets}")
    print(f"  paid this round  : {len(p['paid'])}   skipped (<{p['min_payout_ton']} TON): {len(p['skipped'])}")
    if p["paid"]:
        print("\nPayouts (full share to holder):")
        for r in p["paid"]:
            pct = 100 * r["brt"] / p["total_eligible_brt"]
            print(f"  {_short(r['address'])}  {pct:6.2f}%  ->  {r['ton']:.4f} TON")
    if p["skipped"]:
        print("\nSkipped (rolls to next round):")
        for r in p["skipped"]:
            print(f"  {_short(r['address'])}  would be {r['ton']:.4f} TON")

    print("\n" + "-" * 64)
    print(f"Pool (25% of DEV)      : {p['pool_ton']:.4f} TON")
    print(f"Distributed to holders : {p['total_paid_ton']:.4f} TON  ({len(p['paid'])} transfers)")
    print(f"Gas (project-paid)     : ~{p['gas_estimate_ton']:.4f} TON")
    print(f"Total leaving DEV      : ~{round(p['total_paid_ton'] + p['gas_estimate_ton'], 4):.4f} TON")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows console is cp1250
    except Exception:
        pass
    plan = build_plan()
    print_plan(plan)
    out_dir = ROOT / "data"; out_dir.mkdir(exist_ok=True)
    out = out_dir / f"rewards_plan_{datetime.now(timezone.utc):%Y%m%d}.json"
    out.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"\nPlan written: {out.relative_to(ROOT)}")
    print("READ-ONLY — nothing signed or sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
