#!/usr/bin/env bash
# Stage given paths, commit with given message, and push with rebase
# retry loop. Intended for use inside GitHub Actions where multiple
# concurrent workflows race against `main` and a single push can be
# rejected even if we just pulled.
#
# Special case: scripts/seen.db is a SQLite cache that is regenerable
# from the .md files. When two concurrent runs each commit their own
# version, rebase produces an unmergeable binary conflict. We resolve
# that by keeping the local pending-commit copy (`--theirs` in rebase
# semantics) and continuing.
#
# Usage:
#   bash scripts/git_commit_push.sh "<commit message>" path1 [path2 ...]
#
# Returns 0 if there was nothing to commit OR if push succeeded.
# Returns non-zero only if all retry attempts failed.

set -uo pipefail

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

# Resolve binary conflicts on the regenerable seen.db cache by keeping
# the local pending-commit copy. In rebase semantics "theirs" = the
# commit being applied (ours, in the colloquial sense), while "ours" =
# the upstream branch.
resolve_seen_db_conflict() {
  if git diff --name-only --diff-filter=U | grep -qx 'scripts/seen.db'; then
    echo "Auto-resolving scripts/seen.db conflict (keeping local copy)."
    git checkout --theirs -- scripts/seen.db
    git add scripts/seen.db
    return 0
  fi
  return 1
}

for attempt in 1 2 3 4 5; do
  if git pull --rebase origin main; then
    if git push; then
      echo "Pushed on attempt $attempt."
      exit 0
    fi
  else
    # Rebase paused on conflict — try the seen.db auto-resolver, then
    # continue. If anything else conflicted, abort and retry the loop.
    if resolve_seen_db_conflict; then
      if GIT_EDITOR=true git -c core.editor=true rebase --continue; then
        if git push; then
          echo "Pushed on attempt $attempt after seen.db auto-resolve."
          exit 0
        fi
      else
        echo "rebase --continue failed after seen.db resolve."
        git rebase --abort 2>/dev/null || true
      fi
    else
      echo "Unhandled rebase conflict — aborting and retrying."
      git rebase --abort 2>/dev/null || true
    fi
  fi
  echo "Push attempt $attempt rejected — retrying after backoff."
  sleep $((attempt * 3))
done

echo "ERROR: failed to push after 5 attempts." >&2
exit 1
