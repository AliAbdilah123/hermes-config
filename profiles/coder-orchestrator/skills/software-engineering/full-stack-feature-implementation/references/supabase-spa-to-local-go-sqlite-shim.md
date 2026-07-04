# Supabase SPA to local Go + SQLite shim migration

Use when a React/Vite SPA is tightly coupled to `@supabase/supabase-js` (`supabase.from(...)`, `supabase.auth.*`, `functions.invoke`) and the user asks to migrate it to the local Go + SQLite stack while preserving the existing UI source.

## Pattern

1. Preserve the source repo/frontend as the application source of truth. Do not copy a donor UI.
2. Replace `src/lib/store.ts` with a tiny Supabase-shaped facade instead of editing every caller:
   - `from(table).select().eq().gte().lte().order()` -> `GET /api/<table>?...`
   - `insert`, `update`, `delete`, `single` -> HTTP verbs plus query params
   - `auth.getUser/signUp/signInWithPassword/signOut/updateUser` -> local auth endpoints
   - `functions.invoke(name)` -> `POST /api/functions/<name>`
3. Implement the Go backend endpoints the facade needs:
   - cookie sessions + bcrypt email/password auth
   - SQLite tables matching the Supabase tables used by the SPA
   - table endpoints for the small query/update surface the UI actually uses
   - scoped data access by current user/wallet ownership/shared wallets
   - compatibility responses shaped as `{ data: ... }`
4. Bootstrap the default wallet/account/categories during signup, replacing Supabase auth triggers.
5. For Vite subpath deploys, set `base: '/projects/<slug>/'`; the facade should call `${import.meta.env.BASE_URL}api/...` so it works locally and behind nginx.
6. Add a systemd unit with project-root `.env` as optional `EnvironmentFile`, `ADDR`, and `DB_PATH`; do not store secrets in the unit.
7. Add nginx before the generic `/projects/` fallback:
   - `location ^~ /projects/<slug>/api/ { proxy_pass http://127.0.0.1:<port>/api/; }`
   - `location /projects/<slug>/ { alias /var/www/html/projects/<slug>/; try_files ... }`

## Verification

- `go test ./...`
- `pnpm build`
- Start the API against a temp SQLite DB and smoke:
  - `/api/health`
  - signup
  - `GET /api/wallets` returns one default wallet
  - insert a wallet account
- Deploy assets and verify:
  - public index 200
  - public API health 200
  - signup through the nginx path creates a wallet
  - public index references assets under `/projects/<slug>/assets/...`

## Pitfalls

- If TypeScript callers expect `data.map(...)` inference, a facade returning `any` can create implicit-any errors. Either type the facade result broadly enough or add minimal inline parameter types at the affected `.map/.find` sites.
- Do not use an already-occupied backend port just because another local-stack project uses it; check listeners and allocate a free port.
- If nginx API smoke returns a 404 HTML page but direct backend health works, the API `location` is missing, ordered after a broader fallback, or was not reloaded.
- Runtime SQLite DB files and built Go binaries belong in `.gitignore`; commit source, service template, and migrations/backend code only.
