"""Workflow self-healer.

GitHub Actions scheduled crons are best-effort and on this repo they
silently get skipped for hours at a time. This script runs every 30
minutes from the keepalive workflow and re-fires any scheduled slot
that should have happened in the last few hours but did not.

Logic per workflow:
  1. List recent runs (last 20).
  2. Walk each expected slot in the lookback window.
  3. If no run exists within +/- 60 min of that slot, dispatch the
     workflow once.
  4. At most one re-fire per workflow per healer pass — avoids floods.

Coverage rules:
  - A slot is "covered" by ANY run (scheduled, manual, healer) within
    +/- 60 min, regardless of conclusion. We do not retry failed runs
    here — the failure is the application's problem to fix.
  - Slots inside the GRACE_MIN window from now are skipped — the GH
    scheduler may still be about to deliver them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Per-workflow expected (hour, minute) UTC slots. Keep in sync with the
# `cron:` lines inside each .github/workflows/*.yml file.
CRONS: dict[str, list[tuple[int, int]]] = {
    "telegram-news.yml": [(h, 0) for h in range(24)],
    "telegram-mcap.yml": [(0, 30), (6, 30), (12, 30), (18, 30)],
    "x-news.yml": [(h, 5) for h in range(0, 24, 3)],
    "x-mcap.yml": [(0, 45), (6, 45), (12, 45), (18, 45)],
    "x-fomo.yml": [(9, 15), (19, 15)],
    "update-and-deploy.yml": [
        (h, 0) for h in (0, 2, 4, 6, 8, 10, 11, 14, 16, 17, 20, 22)
    ],
}

GRACE_MIN = 10
LOOKBACK_HOURS = 4
COVERAGE_WINDOW_MIN = 60

# update-and-deploy.yml hour-of-day → blog roundup_kind. Slots not in
# this map are routine news-only runs.
ROUNDUP_KIND_BY_HOUR: dict[int, str] = {
    6: "morning",
    11: "noon",
    17: "evening",
}


def list_runs(workflow: str) -> list[datetime]:
    out = subprocess.check_output(
        [
            "gh", "run", "list",
            f"--workflow={workflow}",
            "--limit=30",
            "--json=createdAt,status,conclusion",
        ],
        text=True,
    )
    runs = json.loads(out)
    times: list[datetime] = []
    for r in runs:
        # Count anything that started — completed-success, completed-failure,
        # or in_progress. A failed run still "covers" the slot for healer
        # purposes; we do not want to spam-retry application bugs.
        ts = r.get("createdAt")
        if not ts:
            continue
        times.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
    return times


def dispatch(workflow: str, fields: dict[str, str] | None = None) -> None:
    cmd = ["gh", "workflow", "run", workflow]
    if fields:
        for k, v in fields.items():
            cmd += ["--field", f"{k}={v}"]
    subprocess.run(cmd, check=True)


def main() -> int:
    now = datetime.now(timezone.utc)
    print(f"[healer] now={now.isoformat()} lookback={LOOKBACK_HOURS}h grace={GRACE_MIN}m")

    fired: list[str] = []

    for workflow, slots in CRONS.items():
        try:
            run_times = list_runs(workflow)
        except subprocess.CalledProcessError as e:
            print(f"[healer] {workflow}: gh run list failed ({e}) — skipping")
            continue

        # Generate expected slot datetimes in lookback window.
        candidates: list[datetime] = []
        for offset_h in range(LOOKBACK_HOURS, -1, -1):
            day = (now - timedelta(hours=offset_h)).date()
            for (h, m) in slots:
                slot = datetime(day.year, day.month, day.day, h, m, tzinfo=timezone.utc)
                if slot > now - timedelta(minutes=GRACE_MIN):
                    continue
                if slot < now - timedelta(hours=LOOKBACK_HOURS):
                    continue
                candidates.append(slot)

        # Sort newest-first — fire the most recent missed slot.
        candidates.sort(reverse=True)

        missed: datetime | None = None
        for slot in candidates:
            covered = any(
                abs((r - slot).total_seconds()) < COVERAGE_WINDOW_MIN * 60
                for r in run_times
            )
            if not covered:
                missed = slot
                break

        if missed is None:
            print(f"[healer] {workflow}: all slots in window covered")
            continue

        fields: dict[str, str] | None = None
        if workflow == "update-and-deploy.yml":
            kind = ROUNDUP_KIND_BY_HOUR.get(missed.hour)
            if kind:
                fields = {"roundup_kind": kind}

        label = f" (kind={fields['roundup_kind']})" if fields else ""
        print(f"[healer] {workflow}: missed slot {missed.isoformat()}{label} — dispatching")
        try:
            dispatch(workflow, fields)
            fired.append(workflow)
        except subprocess.CalledProcessError as e:
            print(f"[healer] {workflow}: dispatch FAILED ({e})")

    print(f"[healer] done — fired={len(fired)}: {fired}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
