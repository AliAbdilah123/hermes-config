#!/bin/bash
# Daily git update for ~/.hermes
cd ~/.hermes || exit 1
git add -A
# Exit silently if nothing to commit
if git diff --cached --quiet; then
  exit 0
fi
git commit -m "daily: $(date +%Y-%m-%d %H:%M)"
git push
echo "✅ Pushed daily update"
