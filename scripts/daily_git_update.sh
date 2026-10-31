#!/bin/bash
# Daily git update for ~/.hermes
cd ~/.hermes || exit 1
# Drop runtime files that were tracked before .gitignore covered them.
git ls-files -ci --exclude-standard -z | xargs -0r git rm -r --cached --ignore-unmatch
git add -A
# Exit silently if nothing to commit
if git diff --cached --quiet; then
  exit 0
fi
git commit -m "daily: $(date +%Y-%m-%d %H:%M)"
git push
echo "✅ Pushed daily update"
