# Brand Organizer migrated-stack parity audit

Use when asked to check parity between the local Brand Organizer React/Vite + Go/SQLite migration and the upstream TypeScript/Cloudflare Worker + Neon implementation.

## Scope framing

- Treat `origin/master` (or the fetched upstream default branch) as the source implementation unless the user names a different branch.
- Treat the local migration branch as a translated stack, not a direct merge target: parity means equivalent user-facing behavior and API capability, not identical files.
- Report gaps explicitly as **not implemented**, **not updated**, **intentionally not applicable**, or **partially mapped**.

## Efficient audit workflow

1. Inspect branch/remotes/history:
   ```bash
   git status --short --branch
   git remote -v
   git branch -vv
   git log --oneline --decorate --graph --all -n 30
   git merge-base HEAD origin/master
   git log --oneline --reverse $(git merge-base HEAD origin/master)..origin/master
   ```

2. Compare file coverage:
   ```bash
   git diff --name-status HEAD..origin/master -- apps/frontend apps/backend apps/backend-go .env.example package.json pnpm-workspace.yaml pnpm-lock.yaml scripts/dev.mjs
   git diff --stat HEAD..origin/master -- apps/frontend apps/backend apps/backend-go .env.example package.json pnpm-workspace.yaml pnpm-lock.yaml scripts/dev.mjs
   comm -13 <(git ls-tree -r --name-only HEAD | sort) <(git ls-tree -r --name-only origin/master | sort) | grep -E '^(apps/frontend/src|apps/backend/src|apps/backend/drizzle|apps/backend/scripts|\.env|package|pnpm|scripts)'
   ```

3. Map frontend gaps by feature, not just filenames:
   - Auth overhaul: Neon Auth provider/client, social sign-in buttons, forgot-password route, shared auth UI components.
   - Analytics instrumentation: PostHog dependency, provider in `main.tsx`, event taxonomy, `track(...)` calls on auth/API/page actions.
   - Theme support: `ThemeProvider`, `ThemeToggle`, topbar wiring, CSS variables/global style deltas.
   - Landing/app shell: blog/FAQ sections, nav/preview/pricing changes, mobile/sidebar/topbar updates.
   - API client: central `apiRequest`, bearer-token/local IG token handling, structured `ApiError`.

4. Map backend gaps by route/capability:
   - Extract upstream route declarations with:
     ```bash
     for f in apps/backend/src/routes/*.ts; do echo "# $f"; git show origin/master:$f | grep -E "\.((get|post|patch|delete)\()"; done
     ```
   - Compare against Go dispatch cases in `apps/backend-go/main.go`.
   - Common upstream features missing from Go migration include hashtags routes, Instagram comments, Instagram sync, Facebook `/api/facebook/oauth/*` route parity, Xendit webhook, observability/metrics/OTel, account-capability feature gates, cron/queue publishing, richer post media/R2 handling, and recovery SQL equivalents.

5. Preserve stack judgments:
   - Do not mark Worker/Neon migrations as blindly missing if they are not applicable to Go/SQLite; instead call out whether their intent has or has not been translated.
   - Do not require upstream Neon Auth to be copied into the Go stack unless the user explicitly wants to abandon local Go auth. Record local auth as a partial/alternative mapping.

## Verification commands

Run the migrated stack checks to ground the audit:

```bash
corepack pnpm --filter frontend typecheck
corepack pnpm --filter frontend test
corepack pnpm --filter frontend build
cd apps/backend-go && go test ./... && go build ./...
```

Report pass/fail plus non-blocking warnings separately from parity gaps. A passing build means the migrated stack is internally healthy; it does not imply upstream parity.

## Reporting format

Recommended sections:

1. Compared branches/commits.
2. Main gaps not implemented / not updated.
3. Implemented or partially mapped items.
4. Verification run and exact results.
5. Bottom line: builds/tests status vs parity status.

For this user, if a public deployment URL is discoverable during the work, end with the public link.