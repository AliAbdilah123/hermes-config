# Self-Flow Cloudflare/Neon to Local Go + SQLite Migration

Use this reference when migrating a cloned Cloudflare Worker + Neon/Stack Auth monorepo to the user's local Go + SQLite + Vite deployment stack while preserving the cloned frontend as source of truth.

## Source shape observed

- Repo: `capt4ce/self-flow-monorepo`
- Web app: `packages/fe` (React 19, Vite, React Router, Tailwind/shadcn, API client in `src/lib/api-client.ts`)
- Cloud backend: `packages/be-serverless` (Hono Worker, `/api/*` routes)
- Shared DTOs: `packages/common/types/*`
- Cloud DB/auth assumptions: Neon/Postgres/Drizzle and Stack Auth
- Mobile packages to preserve untouched: `packages/mobile`, `packages/mobile-capacitor`, `packages/mobile-flutter`

## Migration pattern

1. Clone/preserve the source repo as the target project; do not replace the UI with a boilerplate donor.
2. Add a local backend under `api/v1/` with:
   - `go.mod`
   - `main.go`
   - representative tests (`health`, one CRUD path, one frontend-special endpoint such as subtask counts)
3. Persist local data in project-root `sqlite.db`; a simple JSON state table is sufficient for first-pass local parity:
   - `app_state(id integer primary key check(id=1), payload text not null, updated_at text not null)`
   - seed a demo user plus enough goals/tasks/habits/focus data for the dashboard to render.
4. Implement the API surface actually used by the frontend client before attempting full backend parity:
   - `/api/healthz`
   - `/api/auth/*`, `/api/users/*`
   - `/api/goals`, `/api/goals/:id`, `/api/goals/:id/tasks`
   - `/api/tasks`, `/api/tasks/date/:date`, `/api/tasks/:id`, `/api/tasks/reorder`, `/api/tasks/bulk-update`, `/api/tasks/subtasks`, `/api/tasks/subtask-counts`
   - `/api/task-groups`, `/api/energy`, `/api/habits`, `/api/habits/logs`, `/api/focus`, `/api/focus/graph`
5. Replace the frontend cloud-auth runtime seam with a local demo/session provider unless the user explicitly asks to keep Stack Auth:
   - `AuthContext` returns a stable local user and token.
   - Stack provider wrapper can become a pass-through.
   - Sign-in/sign-up/OAuth callback pages should route into the local session instead of rendering cloud auth widgets.
6. Make Vite subpath-aware:
   - In `vite.config.ts`, set `base: process.env.VITE_BASE_PATH || "/"`.
   - Build with `VITE_BASE_PATH=/projects/<slug>/ VITE_API_URL=/projects/<slug>/api pnpm --filter fe build`.
   - In React Router, set `basename={import.meta.env.BASE_URL}`.
   - In the API client, prefer `import.meta.env.VITE_API_URL || `${import.meta.env.BASE_URL}api`` for production fallback.
7. Deploy isolated service and route:
   - Build Go binary under `api/v1/server`.
   - Systemd service uses `EnvironmentFile=/home/ubuntu/projects/<slug>/.env` instead of embedding secrets.
   - Nginx needs an app-specific `location ^~ /projects/<slug>/api/` before the generic `/projects/` static location.
   - Static files go to `/var/www/html/projects/<slug>/`.
8. Verify no mobile changes:
   - `git diff --name-only -- packages/mobile packages/mobile-capacitor packages/mobile-flutter` should be empty.

## Verification checklist

- `go test ./...` from `api/v1` passes.
- `VITE_BASE_PATH=/projects/<slug>/ VITE_API_URL=/projects/<slug>/api pnpm --filter fe build` passes.
- Systemd service is active and shows the project `.env` as an `EnvironmentFile`.
- Public SPA returns 200.
- Public JS asset referenced by `index.html` returns 200. If it is `/assets/...` instead of `/projects/<slug>/assets/...`, the Vite base path is wrong and the app is not truly subpath-ready.
- Public API health route returns 200 and expected service marker.
- Browser smoke check renders source app markers and seeded data, with no console/page errors.
- Mobile package diff is empty.

## Pitfalls

- Do not rely on `BrowserRouter` alone for subpath deployments. Router links may render, but Vite asset URLs still break unless `base` is set before production build.
- If pnpm blocks install/build due to ignored build scripts after a fresh install, approve required build scripts (`pnpm approve-builds --all`) and rerun install/build. Capture the approval as a setup fix, not as a durable tool failure.
- Generic `/projects/` nginx fallback can serve the SPA but will not proxy the app API. Add the specific API proxy location before the generic static location.
- Browser tool timeouts are not a reason to skip visual/runtime verification. Use an installed Chromium/Playwright executable path if available and verify rendered text plus console errors.
- Do not log or print project-root `.env` contents; verify `EnvironmentFiles=` via `systemctl show` instead.
