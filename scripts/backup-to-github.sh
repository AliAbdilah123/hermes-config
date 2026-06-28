#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/.hermes"

# Ensure repo exists
if [ ! -d .git ]; then
  echo "No git repo found in $HOME/.hermes" >&2
  exit 1
fi

# Configure git user for unattended commits (override in ~/.gitconfig)
git config user.email "backup@local"
git config user.name "hermes-backup"

# Stage everything that respects .gitignore
git add -A

# Commit only if there are changes
if git diff --cached --quiet; then
  echo "Nothing to commit."
  exit 0
fi

git commit -m "backup: $(date '+%Y-%m-%d %H:%M:%S')"

# Push if remote is configured
if git remote get-url origin >/dev/null 2>&1; then
  git push origin main
else
  echo "No remote 'origin' configured. Set it with:
    git remote add origin git@github.com:<user>/<repo>.git"
fi
