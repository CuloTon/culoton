#!/usr/bin/env bash
# Stage given paths, commit with given message, and push with rebase
# retry loop. Intended for use inside GitHub Actions where multiple
# concurrent workflows race against `main` and a single push can be
# rejected even if we just pulled.
#
# Usage:
#   bash scripts/git_commit_push.sh "<commit message>" path1 [path2 ...]
#
# Returns 0 if there was nothing to commit OR if push succeeded.
# Returns non-zero only if all retry attempts failed.

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: git_commit_push.sh <message> <path> [<path>...]" >&2
  exit 2
fi

MSG="$1"
shift
PATHS=("$@")

git config user.name "culoton-bot"
git config user.email "bot@culoton.fun"

git add -- "${PATHS[@]}"

if git diff --cached --quiet; then
  echo "Nothing staged — no commit."
  exit 0
fi

git commit -m "$MSG"

for attempt in 1 2 3 4 5; do
  git pull --rebase --autostash origin main || true
  if git push; then
    echo "Pushed on attempt $attempt."
    exit 0
  fi
  echo "Push attempt $attempt rejected — retrying after backoff."
  sleep $((attempt * 3))
done

echo "ERROR: failed to push after 5 attempts." >&2
exit 1
