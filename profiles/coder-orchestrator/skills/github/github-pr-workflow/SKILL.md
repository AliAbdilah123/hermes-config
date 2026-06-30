---
name: github-pr-workflow
description: "GitHub PR lifecycle: branch, commit, open, CI, merge."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge]
    related_skills: [github-auth, github-code-review]
---

# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle. Each section shows the `gh` way first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

This part is pure `git` — identical either way:

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

## 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

### Direct Push to a Shared Branch (when explicitly requested)

When the user explicitly asks to push all updated code to `master`/`main` instead of opening a PR, do the direct-push flow, but still preserve the same verification discipline:

1. Identify the intended repo from the chat/project context, then confirm with `git status --short --branch` and `git remote -v`.
2. Inspect the change set before staging (`git diff --stat`, targeted diffs). Do not print secret-bearing `.env` values; if env files are already tracked and modified, summarize keys/redacted diffs only.
3. Run the project’s available tests/typechecks/builds before committing. Treat warnings separately from failing exit codes.
4. Remove or ignore generated artifacts created by verification commands before staging (for example Go binaries produced by `go build` inside an app directory, local DBs, caches, `dist/` if ignored). Add durable generated-artifact ignores to `.gitignore` when appropriate.
5. `git fetch origin <branch>` before committing/pushing so the final status shows whether the local branch is based on current remote. If this returns `fatal: couldn't find remote ref <branch>`, do not stop: confirm the local branch and remote heads with `git branch -vv` and `git ls-remote --heads origin`, then proceed with `git push -u origin <branch>` if the local branch is intentionally new.
6. Commit with a conventional message that describes the bundled updates.
7. Push the exact branch requested: `git push origin master` or `git push origin main`. For a current local feature/migration branch with no upstream yet, push it explicitly with `git push -u origin $(git branch --show-current)` unless the user specifically requested pushing to `master`/`main`.
8. Verify the push, not just the local commit: run `git status --short --branch`, `git ls-remote origin refs/heads/<branch>`, and compare it with `git rev-parse HEAD`.
9. Final response should include the branch, commit short SHA, verification commands that passed, any verification commands that failed with a concise reason, and any project public link the user expects.

## 3. Pushing and Creating a PR

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

## 4. Monitoring CI Status

### Check CI Status

**With gh:**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

**With git + curl:**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### Poll Until Complete (git + curl)

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

## 5. Auto-Fixing CI Failures

When CI fails, diagnose and fix. This loop works with either auth method.

### Step 1: Get Failure Details

**With gh:**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### Step 3: Verify

Re-check CI status using the commands from Section 4 above.

### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

## 6. Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. Pull Latest Shared Branch and Restart a Deployed Service

When the user asks to "pull all updates in master/main and restart the service", treat it as a deployment operation, not just a git operation:

1. Identify the repo and runtime service from the project context, then verify with `git status --short --branch`, `git remote -v`, and the service manager (`systemctl cat <service>` / `systemctl status <service>` when systemd is used).
2. Confirm the working tree is clean before pulling. If uncommitted changes exist, inspect and preserve them before `git pull`; do not overwrite local work silently.
3. Fetch and fast-forward only: `git fetch origin <branch> --prune && git pull --ff-only origin <branch>`. Report the final commit SHA.
4. Rebuild the actual deployed artifact before restarting when the service runs a compiled/static artifact rather than the repo directly. Examples: Go API binary copied to `/opt/<app>/`, frontend `dist/` copied to an nginx-served directory, container image rebuilt, etc. Back up the previous runtime artifact when replacing binaries.
5. Restart via the real service manager (`sudo systemctl restart <service>` for systemd) and verify `systemctl is-active <service>` plus recent logs.
6. Run smoke checks against the internal service endpoint and the public routed URL if one exists. For this user's projects, include the public project link in the final update.
7. If tests fail but the runtime build succeeds, do not hide it: deploy only if the requested restart path is otherwise healthy, then clearly report which verification failed and why.

## 8. Remote Access / Push/Pull Blockers

When the repo remote is inaccessible (`Repository not found`, auth denied, or `gh repo view` cannot resolve it), do not let the GitHub blocker erase verified local work, but do not claim an upstream pull/update happened until it is actually fetched.

1. Verify the blocker with both Git and `gh` when available:
   ```bash
   git fetch origin --prune
   gh repo view OWNER/REPO --json nameWithOwner,url,updatedAt,viewerPermission || true
   git ls-remote origin HEAD || true
   git ls-remote git@github.com:OWNER/REPO.git HEAD || true
   ```
2. If the user says they committed a new update but the configured remote is gone/renamed/private, actively search before giving up:
   ```bash
   gh repo list OWNER --limit 100 --json nameWithOwner,url,updatedAt,visibility
   gh repo list CURRENT_GH_USER --limit 100 --json nameWithOwner,url,updatedAt,visibility
   gh search repos "REPO_OR_PROJECT_NAME" --limit 50 --json fullName,url,updatedAt,visibility,description
   gh search commits "KEYWORD author:OWNER_OR_USER author-date:YYYY-MM-DD" --limit 10 --json repository,sha,commit
   ```
   Also inspect local refs for the date range:
   ```bash
   git log --oneline --decorate --all --since='YYYY-MM-DD 00:00' --until='YYYY-MM-DD 23:59'
   ```
3. Keep the distinction clear:
   - If the new upstream commit was found and fetched: proceed with comparison, implementation, verification, and deployment.
   - If it was not found/access is denied: stop and ask for the correct repo URL, branch, commit SHA, or access grant. Do not re-implement guessed changes.
4. If the task also has a deployable/runtime artifact and local verified changes exist, continue with local verification and deployment from the working tree rather than stopping at push failure.
5. Commit local changes with a clear message so the work is recoverable (`git log --oneline -n 3`, `git status --short --branch`).
6. Attempt `git push -u origin HEAD` only after verification; if it fails, report the exact remote URL and error, plus the local commit SHA.
7. In the final response, distinguish clearly between:
   - upstream discovery/pull status (found/fetched or not found/inaccessible),
   - implementation/deployment status (what is actually live and smoke-tested), and
   - GitHub sync status (what could not be pushed because of access/remote state).

This keeps user-facing deliverables moving while preserving an auditable path to pull/push later once the remote/access issue is corrected.

## 8. Complete Workflow Example

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see Section 4)

# 8. Merge when green (see Section 6)
```

## Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` |
| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
