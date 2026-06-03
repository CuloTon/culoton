"""BRAINROT $BRT rewards snapshot — READ-ONLY, no keys, no sending.

Computes the payout PLAN for a reward round. The holder reward is now TWO pools,
each a quarter of the DEV wallet TON balance at snapshot time:

  ALL-holders pool = REWARD_PCT (25%) shared pro-rata across EVERY eligible holder
                     per holder = all_pool * (holder_BRT / total_eligible_BRT)

  TOP-10 pool      = TOP10_PCT (25%) shared pro-rata across ONLY the 10 biggest
                     eligible holders
                     per top holder = top_pool * (holder_BRT / total_top10_BRT)

A holder's reward is the SUM of whatever they get from each pool. A TOP-10 holder
is paid from BOTH pools — once as one of "everyone", and again as one of the top
ten — so the top ten de-facto receive a much larger slice than 25% alone. One
on-chain transfer per holder carries the combined amount.

Rules (mirrored by rewards_payout.py):
  * A round only runs when the DEV balance >= MIN_BANK_TON (4 TON -> pools >= 2 TON).
  * Holders whose COMBINED share < MIN_PAYOUT_TON are skipped — their share rolls
    over (dust would cost more in gas than it's worth).
  * Gas (~GAS_PER_TX each) is paid by the project; holders get their full share.

Excluded from the holder set (and from the TOP 10): the DEV wallet, the jetton
master, the BRAINROT Invest and Marketing treasuries (our own wallets — they hold
$BRT but must not be paid TON back to ourselves), the burn address, and any holder
that is a contract rather than a plain wallet (this removes the DeDust LP pool and
other non-EOA holders).

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

# Treasury split: whatever is left of the bank AFTER both 25% reward pools and a
# 1 TON buffer is split 50/50 between these two project wallets.
INVEST_ADDRESS = "UQDue5ypYa45sG2CO6M_nIFJwpStYpDz3JbCZVeHes10j3n1"     # BRAINROT Invest
MARKETING_ADDRESS = "UQBKy4WDlSLQq5XdSkFvw4QcgETG-gZk6PIXWMHU1R52Yx7w"  # BRAINROT Marketing

REWARD_PCT = 0.25          # 25% of the DEV balance → ALL eligible holders, pro-rata
TOP10_PCT = 0.25           # 25% of the DEV balance → the TOP 10 holders, pro-rata among them
TOP_N = 10                 # how many top holders share the TOP-10 pool
MIN_BANK_TON = 4.0         # a round only runs when DEV balance >= this (pools >= 2 TON)
MIN_PAYOUT_TON = 0.05      # skip holders whose combined share is below this
TREASURY_BUFFER_TON = 1.0  # always leave at least this much on the DEV wallet
MIN_TREASURY_TON = 0.01    # don't bother sending a treasury split below this
GAS_PER_TX = 0.006         # rough network gas per transfer (project-paid)
NANO = 1_000_000_000

TONAPI = "https://tonapi.io/v2"
ROOT = Path(__file__).resolve().parent.parent
# Where the website + Telegram bot read their data from. We drop the simulation
# JSON here too so /simulate and the site can serve it (best-effort — skipped if
# the path doesn't exist on this machine).
SITE_DATA_DIR = Path(r"D:\firma\culoton-fresh\web\src\data")
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
    pool_ton = round(dev_balance_ton * REWARD_PCT, 9)          # 25% → everyone
    top10_pool_ton = round(dev_balance_ton * TOP10_PCT, 9)     # 25% → top 10
    holders_pool_ton = round(pool_ton + top10_pool_ton, 9)     # total to holders (50%)
    gate_open = dev_balance_ton >= MIN_BANK_TON

    master = api_get(f"/accounts/{BRT_MASTER}")
    master_raw = master.get("address", "")

    # Our own project wallets hold $BRT too, but they are NOT holders to reward —
    # rewarding them would just pay TON back to ourselves (and would distort the
    # TOP 10). Resolve each to its raw 0:.. form and exclude it. The Invest and
    # Marketing treasuries are ordinary wallets, so is_plain_wallet() would NOT
    # catch them — they must be named explicitly here.
    project_wallets: dict[str, str] = {}
    for label, friendly in (
        ("DEV wallet", DEV_ADDRESS),
        ("jetton master", BRT_MASTER),
        ("Invest treasury", INVEST_ADDRESS),
        ("Marketing treasury", MARKETING_ADDRESS),
    ):
        try:
            raw = api_get(f"/accounts/{friendly}").get("address", "")
        except Exception:
            raw = ""
        if raw:
            project_wallets[raw.lower()] = label
    # dev_raw / master_raw resolved above are already covered; keep them in sync.
    if dev_raw:
        project_wallets.setdefault(dev_raw.lower(), "DEV wallet")
    if master_raw:
        project_wallets.setdefault(master_raw.lower(), "jetton master")

    holders_resp = api_get(f"/jettons/{BRT_MASTER}/holders?limit=1000")
    raw_holders = holders_resp.get("addresses", [])

    excluded, eligible = [], []
    for h in raw_holders:
        addr = (h.get("owner") or {}).get("address", "")
        bal = int(h.get("balance", 0))
        if bal <= 0 or not addr:
            continue
        low = addr.lower()
        if low in project_wallets:
            excluded.append((addr, bal, project_wallets[low])); continue
        if addr == BURN:
            excluded.append((addr, bal, "burn")); continue
        time.sleep(0.2)
        if not is_plain_wallet(addr):
            excluded.append((addr, bal, "contract / LP pool")); continue
        eligible.append((addr, bal))

    total_elig = sum(b for _, b in eligible)

    # The TOP 10 eligible holders (by $BRT balance) share the TOP-10 pool among
    # themselves; everyone — top 10 included — shares the all-holders pool.
    top10 = sorted(eligible, key=lambda x: x[1], reverse=True)[:TOP_N]
    top10_addrs = {a for a, _ in top10}
    total_top10 = sum(b for _, b in top10)

    paid, skipped = [], []
    if total_elig > 0:
        for addr, bal in eligible:
            all_share = pool_ton * bal / total_elig
            top_share = (top10_pool_ton * bal / total_top10) if (addr in top10_addrs and total_top10 > 0) else 0.0
            total = round(all_share + top_share, 9)
            row = (addr, bal, total, round(all_share, 9), round(top_share, 9), addr in top10_addrs)
            (paid if total >= MIN_PAYOUT_TON else skipped).append(row)
    paid.sort(key=lambda x: x[2], reverse=True)
    skipped.sort(key=lambda x: x[2], reverse=True)

    # Treasury split. We reserve BOTH 25% pools (paid + rolled-over dust) plus a
    # 1 TON buffer on the DEV wallet, then split whatever is left 50/50 between
    # the Invest and Marketing wallets. Gas for every transfer (holders + the two
    # treasury sends) is set aside too so the buffer is never undercut.
    total_paid_ton = round(sum(r[2] for r in paid), 9)
    gas_estimate_ton = round((len(paid) + 2) * GAS_PER_TX, 9)
    treasury_total_ton = round(
        max(0.0, dev_balance_ton - pool_ton - top10_pool_ton - TREASURY_BUFFER_TON - gas_estimate_ton), 9)
    invest_ton = round(treasury_total_ton / 2, 9)
    marketing_ton = round(treasury_total_ton / 2, 9)

    def _row(r):
        a, b, total, al, tp, flag = r
        return {"address": a, "brt": b, "ton": total, "ton_all": al, "ton_top10": tp, "top10": flag}

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dev_address": DEV_ADDRESS, "brt_master": BRT_MASTER,
        "reward_pct": REWARD_PCT, "top10_pct": TOP10_PCT, "top_n": TOP_N,
        "min_bank_ton": MIN_BANK_TON, "min_payout_ton": MIN_PAYOUT_TON,
        "treasury_buffer_ton": TREASURY_BUFFER_TON,
        "invest_address": INVEST_ADDRESS, "marketing_address": MARKETING_ADDRESS,
        "dev_balance_ton": dev_balance_ton,
        "pool_ton": pool_ton, "top10_pool_ton": top10_pool_ton, "holders_pool_ton": holders_pool_ton,
        "gate_open": gate_open,
        "total_eligible_brt": total_elig, "total_top10_brt": total_top10,
        "paid": [_row(r) for r in paid],
        "skipped": [_row(r) for r in skipped],
        "excluded": [{"address": a, "brt": b, "reason": w} for a, b, w in excluded],
        "total_paid_ton": total_paid_ton,
        "gas_estimate_ton": gas_estimate_ton,
        "treasury_total_ton": treasury_total_ton,
        "invest_ton": invest_ton, "marketing_ton": marketing_ton,
    }


SIM_BANK_LEVELS = (25.0, 50.0, 100.0, 500.0)  # hypothetical bank sizes for the simulation


def eligible_from_plan(plan: dict) -> list:
    """Reconstruct the (address, brt) eligible set from a built plan — paid +
    skipped together ARE exactly the eligible holders, contracts/treasuries
    already filtered out."""
    rows = []
    for r in plan.get("paid", []) + plan.get("skipped", []):
        a = r.get("address")
        b = int(r.get("brt", 0))
        if a and b > 0:
            rows.append((a, b))
    return rows


def build_simulation(eligible: list, levels=SIM_BANK_LEVELS, top_sample: int = TOP_N) -> dict:
    """Project what holders would receive at several hypothetical DEV-bank sizes,
    USING THE CURRENT holder distribution. Pure math, no chain calls.

    For each bank size: 25% forms the all-holders pool, 25% the TOP-10 pool, and
    the table shows the combined TON each of the biggest holders would receive
    (TOP 10 are paid from both pools). This is a snapshot of *today's* holders —
    every wallet's number moves as balances change.
    """
    total_elig = sum(b for _, b in eligible)
    ranked = sorted(eligible, key=lambda x: x[1], reverse=True)
    top10 = ranked[:TOP_N]
    top10_addrs = {a for a, _ in top10}
    total_top10 = sum(b for _, b in top10)

    out_levels = []
    for bank in levels:
        all_pool = bank * REWARD_PCT
        top_pool = bank * TOP10_PCT
        treasury = max(0.0, bank - all_pool - top_pool - TREASURY_BUFFER_TON)
        rows = []
        for rank, (addr, bal) in enumerate(ranked[:top_sample], 1):
            all_share = all_pool * bal / total_elig if total_elig else 0.0
            top_share = (top_pool * bal / total_top10) if (addr in top10_addrs and total_top10) else 0.0
            rows.append({
                "rank": rank, "address": addr, "brt": bal,
                "pct": round(100 * bal / total_elig, 4) if total_elig else 0.0,
                "ton_all": round(all_share, 9), "ton_top10": round(top_share, 9),
                "ton": round(all_share + top_share, 9), "top10": addr in top10_addrs,
            })
        out_levels.append({
            "bank": bank,
            "all_pool_ton": round(all_pool, 9), "top10_pool_ton": round(top_pool, 9),
            "holders_pool_ton": round(all_pool + top_pool, 9), "treasury_ton": round(treasury, 9),
            "top": rows,
        })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "based_on": "current holders",
        "n_eligible": len(eligible), "top_n": TOP_N,
        "total_eligible_brt": total_elig, "total_top10_brt": total_top10,
        "reward_pct": REWARD_PCT, "top10_pct": TOP10_PCT,
        "treasury_buffer_ton": TREASURY_BUFFER_TON,
        "levels": out_levels,
    }


def _short(a: str) -> str:
    return a[:10] + "…" + a[-6:] if len(a) > 18 else a


def print_plan(p: dict) -> None:
    print(f"BRAINROT rewards snapshot  ({p['generated_at']})")
    print("-" * 64)
    print(f"DEV wallet balance : {p['dev_balance_ton']:.4f} TON")
    print(f"All-holders pool   : {p['pool_ton']:.4f} TON  (25%, pro-rata across everyone)")
    print(f"TOP-{p['top_n']} pool       : {p['top10_pool_ton']:.4f} TON  (25%, pro-rata across the {p['top_n']} biggest)")
    print(f"Holder total (50%) : {p['holders_pool_ton']:.4f} TON")
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
        print("\nPayouts (full combined share to holder; ★ = TOP 10, gets both pools):")
        for r in p["paid"]:
            pct = 100 * r["brt"] / p["total_eligible_brt"]
            star = "★" if r.get("top10") else " "
            if r.get("top10") and r.get("ton_top10"):
                extra = f"  (all {r['ton_all']:.4f} + top10 {r['ton_top10']:.4f})"
            else:
                extra = ""
            print(f"  {star} {_short(r['address'])}  {pct:6.2f}%  ->  {r['ton']:.4f} TON{extra}")
    if p["skipped"]:
        print("\nSkipped (rolls to next round):")
        for r in p["skipped"]:
            print(f"  {_short(r['address'])}  would be {r['ton']:.4f} TON")

    print("\n" + "-" * 64)
    print(f"All-holders pool (25%) : {p['pool_ton']:.4f} TON")
    print(f"TOP-{p['top_n']} pool (25%)     : {p['top10_pool_ton']:.4f} TON   (★ holders also share this)")
    print(f"Distributed to holders : {p['total_paid_ton']:.4f} TON  ({len(p['paid'])} transfers)")
    print(f"\nTreasury split (rest after both 25% pools + {p['treasury_buffer_ton']:.0f} TON buffer, 50/50):")
    print(f"  BRAINROT Invest      : {p['invest_ton']:.4f} TON  ->  {_short(p['invest_address'])}")
    print(f"  BRAINROT Marketing   : {p['marketing_ton']:.4f} TON  ->  {_short(p['marketing_address'])}")
    leaving = round(p['total_paid_ton'] + p['treasury_total_ton'] + p['gas_estimate_ton'], 4)
    print(f"\nGas (project-paid)     : ~{p['gas_estimate_ton']:.4f} TON")
    print(f"Total leaving DEV      : ~{leaving:.4f} TON  (stays: ~{round(p['dev_balance_ton'] - leaving, 4):.4f} TON = buffer + rolled)")


def print_simulation(sim: dict) -> None:
    print("\n" + "=" * 64)
    print(f"SIMULATION — based on current holders ({sim['n_eligible']} eligible)")
    print("What holders would get at different DEV-bank sizes (25%+25% model):")
    for lv in sim["levels"]:
        print(f"\nBank {lv['bank']:.0f} TON  →  holders {lv['holders_pool_ton']:.2f} TON "
              f"(all {lv['all_pool_ton']:.2f} + top10 {lv['top10_pool_ton']:.2f}), "
              f"treasury ~{lv['treasury_ton']:.2f} TON")
        for r in lv["top"][:5]:
            star = "★" if r["top10"] else " "
            print(f"   {star} #{r['rank']} {_short(r['address'])}  {r['pct']:5.2f}%  ->  {r['ton']:.3f} TON")


def write_simulation(sim: dict) -> None:
    """Write rewards_simulation.json to data/ and (best-effort) the site/bot data
    dir, so the website and the /simulate bot command can serve it."""
    payload = json.dumps(sim, indent=2, ensure_ascii=False)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "rewards_simulation.json").write_text(payload, encoding="utf-8")
    try:
        if SITE_DATA_DIR.exists():
            (SITE_DATA_DIR / "rewards_simulation.json").write_text(payload, encoding="utf-8")
            print(f"Simulation written: {SITE_DATA_DIR / 'rewards_simulation.json'}")
    except Exception as e:
        print(f"(site simulation copy skipped: {e})")


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

    # Simulation across hypothetical bank sizes, reusing the holders we already
    # fetched (paid + skipped = the eligible set) — no extra chain calls.
    sim = build_simulation(eligible_from_plan(plan))
    print_simulation(sim)
    write_simulation(sim)

    print("\nREAD-ONLY — nothing signed or sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
