
#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-.}"
shift || true
PATTERN="${1:-profiles/*/home/.local/share/pnpm/**}"
echo "repo=$REPO"
echo "pattern=$PATTERN"
cd "$REPO"

echo '--- Check for git-filter-repo ---'
if command -v git-filter-repo >/dev/null 2>&1; then
  echo 'Using git-filter-repo'
  git filter-repo --invert-paths --path-glob "$PATTERN"
  exit 0
fi

echo '--- git-filter-repo not found; falling back to git filter-branch ---'
git filter-branch -f \
  --index-filter "git rm -r --cached --quiet --ignore-unmatch $PATTERN" \
  --prune-empty --tag-name-filter cat -- --all

echo '--- Cleanup reflog/refs and GC ---'
git reflog expire --expire-unreachable=now --all || true
git prune || true
git gc --prune=now --aggressive || true

echo '--- Verify ---'
count=$(git ls-tree -r HEAD --name-only | grep -c '^profiles/[^/]\+/home/.local/share/pnpm/' || true)
echo "pnpm_tracked_count=$count"
