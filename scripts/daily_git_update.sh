#!/bin/bash
set -e
# Daily git update for ~/.hermes
cd ~/.hermes
# Drop runtime files that were tracked before .gitignore covered them.
git ls-files -ci --exclude-standard -z | xargs -0r git rm -r --cached -q --ignore-unmatch
git add -A
# Exit silently if nothing to commit
if git diff --cached --quiet; then
  exit 0
fi
git commit -m "daily: $(date '+%Y-%m-%d %H:%M')"
git push -u origin main
echo "✅ Pushed daily update"
