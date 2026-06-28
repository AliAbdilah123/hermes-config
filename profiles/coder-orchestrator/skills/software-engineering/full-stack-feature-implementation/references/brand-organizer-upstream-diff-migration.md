# Brand Organizer upstream diff migration (TS/Cloudflare -> Go/SQLite stack)

Use when asked to pull the latest upstream Brand Organizer branch and migrate the delta into the local Go/SQLite stack.

## Durable workflow

1. **Fetch first, then identify the true upstream branch**
   - Run `git fetch origin --prune`.
   - This repo may use `origin/master` even when the user says `main`; inspect remotes/branches rather than assuming the branch name.

2. **Find the already-migrated boundary**
   - Inspect local migration branch history and upstream history with `git log --oneline --decorate --graph --all` and `git merge-base HEAD origin/<branch>`.
   - The “latest commit migrated” may be a local port/migration commit rather than the upstream merge-base. Compare the upstream commits after the last migrated point with the current remote tip.
   - Use `git diff --name-status <last-migrated-upstream>..origin/<branch>` and per-commit `git show --stat` to separate runtime changes from docs/assets/tooling.

3. **Translate, don’t blindly apply**
   - Apply docs, screenshots, ignore rules, and agent/tool config files directly when they are stack-agnostic.
   - Translate app behavior into Go/SQLite only when there is an equivalent runtime path.
   - Do not copy Cloudflare Worker/Neon-specific implementation details into the Go stack without an equivalent service mechanism.

4. **Brand Organizer-specific migration judgments**
   - Cloudflare Worker cron trigger changes in `apps/backend/wrangler.toml` / Worker `scheduled()` handlers do not directly apply to the Go/SQLite stack unless a Go scheduler/daemon is being added.
   - Upstream migrations that drop legacy TS auth tables such as `users` and `sessions` must not be applied to the Go SQLite DB when those tables are active application tables in `apps/backend-go/main.go`.
   - Facebook/Instagram OAuth changes should be mapped through the Go config layer and `.env.example` aliases (`FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `FACEBOOK_REDIRECT_URI`, graph version), preserving mock/degraded local behavior.

5. **Verify the stack actually still works**
   - Backend: run `go test ./...` and `go build ./...` from `apps/backend-go`.
   - Frontend: run `corepack pnpm --filter frontend typecheck`, `corepack pnpm --filter frontend build`, and the frontend tests from the repo root.
   - If plain `pnpm` is unavailable but Corepack exists, use `corepack pnpm` rather than treating the missing global binary as a blocker.

6. **Deploy from the translated stack, not the repo root**
   - Build the Go service inside `apps/backend-go`; `go build` from the repo root can fail because the Go module is nested.
   - Before copying frontend artifacts, confirm the active nginx/static alias (commonly `/var/www/html/projects/brand-organizer/` for `/projects/brand-organizer/`) and verify the deployed `index.html` plus referenced JS/CSS assets return 2xx.
   - For the systemd-backed Go API, rebuild a binary from `apps/backend-go`, replace `/opt/brand-organizer/brand-organizer-server` with a backup, restart `brand-organizer`, then smoke-test both the backend port and the proxied `/projects/brand-organizer/api/v1/health` path. If the proxy path fails but the backend port works, inspect nginx path rewriting before declaring the API broken.

## Feature-specific translation notes from recent migrations

- Keep `Plans` in the main app sidebar even if upstream latest sidebar omits it; this local stack still exposes `/app/plans` and the user's workflow depends on it.
- When migrating the latest Settings UX, prefer a real second sidebar controlled by `?tab=` (`Profile`, `Instagram Accounts`, `Billing & Plan`, `Notifications`, `Danger Zone`) over a cramped horizontal tabs rail. Desktop should be a vertical sticky nav; mobile should be stacked full-width section buttons.
- Upstream `posts.error_message` maps cleanly to the Go/SQLite stack as an `error_message TEXT` column plus an `errorMessage` API field. Add an idempotent SQLite `ALTER TABLE` during migration for existing deployments, and preserve the Cloudflare/Neon migration file as upstream-only context rather than copying the whole backend stack.
- Use local stack helpers when porting upstream frontend code: `getApiBase()`/`apiRequest()` as available, `authClient` instead of upstream auth clients, and `cn` from `@/lib/utils` for conditional class composition.

## Reporting

Report the upstream remote tip, the local commit made, what was translated vs intentionally skipped, deployment status, and the exact verification results. If push fails due to repository permissions, report it as a delivery blocker without saving it as a durable project rule.
