#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$HOME/.hermes-backups/hermes-config"
SOURCE_HOME="$HOME/.hermes"
COMMIT_MSG="${1:-backup: update hermes config}"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "ERROR: missing repo at $REPO_DIR" >&2
  exit 1
fi

mkdir -p "$REPO_DIR"

rsync -a \
  --delete \
  --exclude='node_modules' \
  --exclude='node' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='logs' \
  --exclude='.git' \
  --exclude='.gitignore' \
  --exclude='*.db' \
  --exclude='*.db-shm' \
  --exclude='*.db-wal' \
  --exclude='*.lock' \
  --exclude='gateway.pid' \
  --exclude='.hermes_history' \
  --exclude='.skills_prompt_snapshot.json' \
  "$SOURCE_HOME/" "$REPO_DIR/"

cd "$REPO_DIR"

git add -A

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "$COMMIT_MSG"
git push origin HEAD
