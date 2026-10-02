#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------
# Backup script for local config directories (e.g. ~/.hermes)
# - Stages changes respecting .gitignore
# - Commits only when there are changes
# - Pushes to origin/main if remote is configured
# ----------------------------------------------------------------------

TARGET_DIR="${1:-$HOME/.hermes}"
REMOTE_BRANCH="${2:-main}"

cd "$TARGET_DIR"

# Safety: require a git repo
if [ ! -d .git ]; then
  echo "No git repo found in $TARGET_DIR" >&2
  exit 1
fi

# Configure unattended commit identity (override via global ~/.gitconfig)
git config user.email "backup@local"
git config user.name "hermes-backup"

# Stage everything that respects .gitignore
git add -A

# Commit only when there are changes
if git diff --cached --quiet; then
  echo "Nothing to commit."
  exit 0
fi

TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "backup: $TIMESTAMP"

# Push if remote exists
if git remote get-url origin >/dev/null 2>&1; then
  git push origin "$REMOTE_BRANCH"
else
  echo "No remote 'origin' configured. Set it with:"
  echo "  git remote add origin git@github.com:<user>/<repo>.git"
fi
