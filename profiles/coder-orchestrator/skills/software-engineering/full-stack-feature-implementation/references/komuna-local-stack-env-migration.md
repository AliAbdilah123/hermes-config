# Komuna local-stack env migration pattern

Use this when migrating Komuna from the original Cloudflare Worker/Neon style project into the local Go + SQLite + Vite stack while keeping env updates easy.

## Durable pattern

- Keep project-specific `.env` and `sqlite.db` at the project root, not inside `api/`, unless the user explicitly asks otherwise.
- Do not print `.env` values. If an existing service env file must be migrated, copy/transform values by key name only and report only the resulting `EnvironmentFile` path/status.
- Prefer local-stack env names but accept original/legacy names as aliases so the user can update env later without rediscovering mappings:
  - `ADDR` preferred; also accept `HOST` + `PORT`.
  - `DATABASE_PATH` preferred; also accept `SQLITE_DB_PATH` and legacy `KOMUNA_DB_PATH`.
  - `CORS_ORIGINS` preferred because it matches the original Worker env; also accept legacy local `ALLOWED_ORIGINS`.
  - `KOMUNA_ADMIN_TOKEN` preferred; also accept `ADMIN_TOKEN`.
  - Frontend should honor `VITE_API_BASE_URL` when set, otherwise use same-origin `/api/v1` or the project path proxy `/projects/Komuna/api/v1`.
- Add/keep `.env.example` with key names only and no secrets. `.gitignore` should ignore `.env`, `.env.*`, `sqlite.db`, and SQLite WAL/SHM files while allowing `.env.example`.
- Update deployment docs to show `EnvironmentFile=<project-root>/.env` rather than copying secret values into the unit.

## Verification checklist

1. Backend: `gofmt`, `go test ./...`, and `go build -o server .` from the Go API directory.
2. Frontend: `npm run lint` and `npm run build` from the Vite frontend directory.
3. Service: `systemctl show <service> -p EnvironmentFiles -p ActiveState -p WorkingDirectory --no-pager` and do not dump env contents.
4. Runtime: curl health/ready/bootstrap through localhost and public nginx proxy.
5. Deployment: verify the nginx alias/root actually serving the public URL, sync `frontend/dist`, then curl public index and referenced JS/CSS assets for 2xx.

## Pitfalls

- Do not wholesale-copy another project/boilerplate over Komuna. Preserve the cloned Komuna application source, especially `apps/web`, and port only stack/runtime seams. If the page looks like `komuna-old`, remove donor frontend files and redeploy from the cloned repo's `apps/web`.
- If Komuna's migrated public UI looks like `komuna-old`, treat that as a source-of-truth failure: restore the frontend to the cloned repo's `apps/web`, build/deploy `apps/web/dist`, and add only the backend/API compatibility seams needed by the upstream frontend.
- For nginx subpath deployment (`/projects/komuna/`), set both Vite `base` and React Router `basename`; missing `basename` can render NotFound/blank while all assets still return HTTP 200.
- Match the original app's runtime state before judging visual parity: if the reference screenshot is dark/logged-in, provide equivalent local theme/session/workspace fallbacks when real Neon Auth is absent.
- Verify visual parity with a mobile viewport/DOM markers from the original UI, not just curl 200s or desktop screenshots. Check for `Pesan pertemuan`, `Program tersedia`, and absence of `Halaman tidak ditemukan` / `Gagal memuat program`.
- If root-absolute public assets like `/komuna-logo.svg` 404 after subpath deployment, copy or alias them explicitly in nginx/static assets.
- If Neon Auth is not configured in the local stack, provide a safe no-auth fallback for public browsing rather than letting `/api/auth/get-session` 404s break the app.
- Verify with a real browser/DOM/screenshot and original app text markers, not only curl/build output. Check mobile viewport too if the user reports a phone blank page.
- Avoid hardcoding a single deployment port into code; let service env define it.
- If a default port is occupied, use a temporary port only for smoke testing. Do not turn that transient collision into a durable rule.
