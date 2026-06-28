# SocialZen full migration to Go/SQLite stack

Use when asked to clone `ibrahim-idrus/Scheduling-Post` as `socialzen` and migrate it from the upstream TS/Cloudflare/Neon stack into the local Go/SQLite stack.

## Durable workflow

1. **Clone and inspect without leaking env values**
   - Clone to `/home/ubuntu/socialzen` unless the user specifies another path.
   - Inspect `/var/lib/socialzen/.env` by key name or an allowlist only. It may be root-readable; use `sudo -n` for key-name/allowlisted reads, never dump secrets.
   - Useful allowlist for deploy wiring: `ADDR`, `DATABASE_PATH`, `MEDIA_DIR`, `PUBLIC_BASE_URL`, `FRONTEND_BASE_URL`, `VITE_API_BASE_URL`.

2. **Migrate the stack, not just the branch name**
   - The source of truth for SocialZen application code is the cloned `Scheduling-Post` git repo/current upstream commit, **not** any previous Brand Organizer working tree. Do not wholesale-copy Brand Organizer frontend files into SocialZen.
   - If you need a known Go/SQLite implementation as a reference, use it as a reference only: port backend capabilities and integration seams deliberately, then compare changed frontend files against the git source-of-truth before committing.
   - Replace the Cloudflare Worker backend (`apps/backend`, Wrangler, Durable Objects, Neon/Drizzle code) with a local `apps/backend-go` Go/SQLite backend.
   - When a task plan or pasted spec references the old Cloudflare/TypeScript implementation (`apps/backend/src`, Hono routes, KV bindings, Wrangler), translate the product behavior into the active Go/SQLite stack instead of creating a parallel stale backend. For example, add routes to `apps/backend-go/main.go`, use local/server-side cache or SQLite-appropriate equivalents for KV-only requirements, and keep the public API contract stable for the React app.
   - Keep the React/Vite frontend from the git repo and adapt only the necessary integration seams: API helpers/auth calls, Vite `base`/proxy, env defaults, and tests for the deployment slug `/projects/socialzen`.
   - Search and replace stale project slug/name references only where they are deployment/config defaults (`brand-organizer`, `Brand Organizer`); avoid visual/content regressions caused by copying another project.
   - After migration, explicitly audit diffs such as `Sidebar.tsx`, landing pages, and layout/theme files. If a frontend diff is not required by the stack change, restore it from git before deployment.
   - Update the Go module name to `socialzen/backend-go`; do not commit built binaries accidentally.

3. **Wire `/var/lib/socialzen/.env` for runtime**
   - Make the Go backend load `/var/lib/socialzen/.env` in addition to local `.env` files.
   - Update non-secret deployment values in `/var/lib/socialzen/.env` to SocialZen paths/URLs, preserving secrets:
     - `ADDR=127.0.0.1:<free-port>`
     - `DATABASE_PATH=/var/lib/socialzen/socialzen.db`
     - `MEDIA_DIR=/var/lib/socialzen/media`
     - `PUBLIC_BASE_URL=<host>/projects/socialzen`
     - `FRONTEND_BASE_URL=<host>/projects/socialzen`
     - `VITE_API_BASE_URL=/projects/socialzen`
   - Back up the env file before editing and avoid printing secret values.

4. **Verify before deployment**
   - Run:
     - `corepack pnpm install --no-frozen-lockfile` if lockfile/package graph changed.
     - `corepack pnpm --filter frontend typecheck`
     - `corepack pnpm --filter frontend test`
     - `corepack pnpm --filter frontend build`
     - `cd apps/backend-go && go test ./... && go build ./...`
   - For API features added to the Go backend, also run a real HTTP smoke against an isolated temp DB when possible: start `apps/backend-go` with `ADDR=127.0.0.1:<free-port> DATABASE_PATH=$(mktemp -d)/socialzen.db MEDIA_DIR=$(mktemp -d)/media`, curl the new endpoint with the demo session cookie, assert response shape, then kill the background process. Do not rely on unit tests alone for route dispatch/auth/path-prefix behavior.
   - If tests fail from stale old-slug expectations, update tests to the new project slug and rerun the whole verification set.
   - For subpath deployments (`/projects/socialzen/`), ensure React Router is mounted with the Vite base URL, e.g. `<BrowserRouter basename={import.meta.env.BASE_URL}>`. Without this, assets can load successfully while React renders a blank app because `/projects/socialzen/` does not match the `/` route.
   - Do not trust HTTP 200 on `index.html` and assets alone. Use a browser/headless render probe (or equivalent DOM text check) to confirm the landing page actually mounts and contains expected copy.

5. **Deploy the translated app**
   - Pick a port that does not collide with existing services (`brand-organizer` may already use `127.0.0.1:8088`).
   - Install backend binary to `/opt/socialzen/socialzen-server` and create `socialzen.service` with `EnvironmentFile=/var/lib/socialzen/.env`.
   - Copy frontend build to `/var/www/html/projects/socialzen/`.
   - Add nginx locations for:
     - `/projects/socialzen/api/` → backend `/api/`
     - `/projects/socialzen/media/` → backend `/media/`
     - `/projects/socialzen/` → static frontend alias
   - Run `nginx -t`, reload nginx, start/restart `socialzen.service`.

6. **Post-deploy smoke tests**
   - `systemctl is-active socialzen`
   - direct API health: `curl -fsS http://127.0.0.1:<port>/health`
   - proxied API health: `curl -fsS http://127.0.0.1/projects/socialzen/api/health`
   - public frontend index and referenced asset URLs return 2xx.

## Pitfalls

- Do not leave `/projects/brand-organizer` defaults in frontend tests, auth/login routes, Vite base, or backend `projectPrefix`.
- Do not deploy the Go backend from the repo root; the Go module is nested in `apps/backend-go`.
- Do not commit generated backend binaries such as `apps/backend-go/backend-go`.
- If `git commit` fails due missing identity in a fresh clone, set a repo-local identity (`git config user.name`, `git config user.email`) and retry.
- The env file may initially contain copied Brand Organizer paths. Treat those as deployment config to adapt, not as immutable project facts.
- A blank page at `/projects/socialzen/` with 200 responses for `index.html` and JS/CSS commonly indicates a client-side routing basename mismatch. Confirm the mounted DOM, not just network status.
- When the user calls out unexpected diffs (for example `Sidebar.tsx`), stop and compare against the git source-of-truth commit immediately; do not defend template-derived changes as migration work unless they are strictly necessary.
