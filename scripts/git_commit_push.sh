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

# Resolve binary conflicts on regenerable SQLite caches (scripts/*.db)
# by keeping the local pending-commit copy. These dbs are dedup state
# that can be rebuilt from .md files / sent messages, so a small loss
# is acceptable — better than killing the whole pipeline. In rebase
# semantics "theirs" = the commit being applied (ours, colloquially),
# while "ours" = the upstream branch.
resolve_db_conflicts() {
  local conflicted resolved=0
  conflicted=$(git diff --name-only --diff-filter=U)
  if [ -z "$conflicted" ]; then return 1; fi
  while IFS= read -r f; do
    case "$f" in
      scripts/*.db)
        echo "Auto-resolving $f conflict (keeping local copy)."
        git checkout --theirs -- "$f"
        git add -- "$f"
        resolved=1
        ;;
    esac
  done <<< "$conflicted"
  [ $resolved -eq 1 ]
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
    if resolve_db_conflicts; then
      if GIT_EDITOR=true git -c core.editor=true rebase --continue; then
        if git push; then
          echo "Pushed on attempt $attempt after db auto-resolve."
          exit 0
        fi
      else
        echo "rebase --continue failed after db resolve."
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
