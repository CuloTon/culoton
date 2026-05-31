"""BRAINROT $BRT rewards payout — Model A (you sign locally).

Sends the weekly/on-demand reward round from the DEV wallet to $BRT holders,
using the plan from rewards_snapshot.build_plan(). The mnemonic is read at
runtime (env DEV_MNEMONIC or a hidden prompt) and NEVER stored or printed.

Guards (it refuses to send unless ALL hold):
  * the wallet derived from the mnemonic must equal DEV_ADDRESS,
  * the bank must be >= MIN_BANK_TON (4 TON),
  * there must be at least one holder above MIN_PAYOUT_TON.

Modes:
  (default)      dry-run — show the plan, send nothing.
  --send         actually send the round (asks for confirmation first).
  --test-self    send a tiny 0.01 TON to the DEV wallet itself to prove
                 signing/sending works, before a real round.
  --yes          skip the typed confirmation.
  --limit N      only pay the top N holders (cautious first run).
  --no-announce  don't post the Telegram summary.

After sending it posts a Telegram summary (who got paid, who rolled over,
bank left) via `gh workflow run tg-announce.yml`, and writes a round log to
data/rewards_round_<UTCdatetime>.json.

Requires: pip install pytoniq   (the .bat wrapper installs it for you)
Run via:  wyplata-nagrod.bat   (double-click) — or: python scripts/rewards_payout.py --send
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

from rewards_snapshot import (
    build_plan, print_plan, DEV_ADDRESS, MIN_BANK_TON, NANO, GAS_PER_TX, ROOT,
)

TEST_SELF_TON = 0.01
CHUNK = 4  # WalletV4R2 sends up to 4 messages per signed transaction


def load_mnemonic() -> list[str]:
    raw = os.getenv("DEV_MNEMONIC", "").strip()
    if not raw:
        print("\nPaste the DEV wallet 24-word seed phrase (input hidden, never stored):")
        raw = getpass("seed > ").strip()
    words = raw.split()
    if len(words) not in (12, 24):
        print(f"ERROR: expected 12 or 24 words, got {len(words)}.", file=sys.stderr)
        sys.exit(2)
    return words


async def open_wallet(provider, mnemo):
    """Try common wallet versions; return the one whose address == DEV_ADDRESS."""
    from pytoniq import WalletV4R2, WalletV5R1, WalletV3R2  # type: ignore
    from pytoniq_core import Address  # type: ignore
    want = Address(DEV_ADDRESS).to_str(is_user_friendly=False)
    for cls in (WalletV4R2, WalletV5R1, WalletV3R2):
        try:
            w = await cls.from_mnemonic(provider=provider, mnemonics=mnemo)
            if w.address.to_str(is_user_friendly=False) == want:
                print(f"Wallet matched: {cls.__name__}")
                return w
        except Exception as e:
            print(f"  ({cls.__name__} did not match: {type(e).__name__})")
    return None


def confirm(skip: bool, prompt: str) -> bool:
    if skip:
        return True
    return input(prompt).strip().upper() in ("TAK", "YES", "Y")


def post_telegram(summary: str) -> None:
    try:
        subprocess.run(
            ["gh", "workflow", "run", "tg-announce.yml", "-R", "CuloTon/culoton",
             "-f", f"message={summary}"],
            check=True, cwd=ROOT, capture_output=True, text=True,
        )
        print("Telegram summary dispatched.")
    except Exception as e:
        print(f"(Telegram post skipped: {e})")


def build_summary(round_no: int, paid: list, skipped: list, total_paid: float, bank_left: float) -> str:
    top = "\n".join(f"• {r['address'][:6]}…{r['address'][-4:]} — {r['ton']:.3f} TON" for r in paid[:10])
    more = f"\n…and {len(paid) - 10} more" if len(paid) > 10 else ""
    return (
        f"💸 <b>$BRT rewards — round #{round_no}</b>\n\n"
        f"Distributed <b>{total_paid:.3f} TON</b> to <b>{len(paid)}</b> holders, "
        f"pro-rata to their $BRT.\n{top}{more}\n\n"
        f"⏳ {len(skipped)} holders rolled over (share below 0.05 TON — accumulating for next round).\n"
        f"🏦 Bank now ~{bank_left:.2f} TON. The more $BRT you hold, the bigger your share. "
        f"Details: https://brainrot-ton.fun/rewards"
    )


async def run(args) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    send = "--send" in args
    test_self = "--test-self" in args
    skip_confirm = "--yes" in args
    announce = "--no-announce" not in args
    limit = None
    if "--limit" in args:
        try:
            limit = int(args[args.index("--limit") + 1])
        except Exception:
            print("ERROR: --limit needs a number.", file=sys.stderr); return 2

    print("Computing live plan…\n")
    plan = build_plan()
    print_plan(plan)

    if not (send or test_self):
        print("\nDRY-RUN — nothing sent. Re-run with --send to pay, or --test-self to validate.")
        return 0

    # --- guards ---
    if not plan["gate_open"]:
        print(f"\nABORT: bank {plan['dev_balance_ton']:.3f} TON is below {MIN_BANK_TON} TON. "
              f"No round runs yet.")
        return 1
    paid = plan["paid"][:limit] if limit else plan["paid"]
    if send and not paid:
        print("\nABORT: no holder is above 0.05 TON this round — everything rolls over.")
        return 1

    try:
        from pytoniq import LiteBalancer  # type: ignore
        from pytoniq_core import Address  # type: ignore
    except ImportError:
        print("\nERROR: pytoniq is not installed. Run:  pip install pytoniq", file=sys.stderr)
        return 2

    mnemo = load_mnemonic()
    provider = LiteBalancer.from_mainnet_config(trust_level=2)
    await provider.start_up()
    try:
        wallet = await open_wallet(provider, mnemo)
        if wallet is None:
            print("\nABORT: the seed phrase does not control the DEV wallet "
                  f"({DEV_ADDRESS}). Nothing sent.", file=sys.stderr)
            return 1

        if test_self:
            if not confirm(skip_confirm, f"\nSend a {TEST_SELF_TON} TON self-test to DEV? type TAK: "):
                print("Cancelled."); return 0
            msg = wallet.create_wallet_internal_message(
                destination=Address(DEV_ADDRESS), value=int(TEST_SELF_TON * NANO), body="brt-rewards-selftest")
            await wallet.raw_transfer(msgs=[msg])
            print(f"Self-test sent ({TEST_SELF_TON} TON). Check the DEV wallet — if it arrived, signing works.")
            return 0

        total_paid = round(sum(r["ton"] for r in paid), 9)
        print(f"\nABOUT TO SEND {total_paid:.4f} TON to {len(paid)} holders from {DEV_ADDRESS}.")
        if not confirm(skip_confirm, "Type TAK to send (anything else cancels): "):
            print("Cancelled — nothing sent."); return 0

        sent = 0
        for i in range(0, len(paid), CHUNK):
            chunk = paid[i:i + CHUNK]
            msgs = [
                wallet.create_wallet_internal_message(
                    destination=Address(r["address"]), value=int(round(r["ton"] * NANO)))
                for r in chunk
            ]
            await wallet.raw_transfer(msgs=msgs)
            sent += len(chunk)
            print(f"  sent {sent}/{len(paid)} …")
            await asyncio.sleep(2)

        bank_left = round(plan["dev_balance_ton"] - total_paid - len(paid) * GAS_PER_TX, 4)
        print(f"\nDONE: {total_paid:.4f} TON to {len(paid)} holders. Bank ~{bank_left:.2f} TON.")

        # round log
        round_no = len(list((ROOT / "data").glob("rewards_round_*.json"))) + 1
        log = {"round": round_no, "at": datetime.now(timezone.utc).isoformat(),
               "total_paid_ton": total_paid, "paid": paid, "skipped": plan["skipped"],
               "bank_before": plan["dev_balance_ton"], "bank_after_est": bank_left}
        (ROOT / "data").mkdir(exist_ok=True)
        (ROOT / "data" / f"rewards_round_{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json").write_text(
            json.dumps(log, indent=2), encoding="utf-8")

        if announce:
            post_telegram(build_summary(round_no, paid, plan["skipped"], total_paid, bank_left))
        return 0
    finally:
        await provider.close_all()


if __name__ == "__main__":
    sys.exit(asyncio.run(run(sys.argv[1:])))
