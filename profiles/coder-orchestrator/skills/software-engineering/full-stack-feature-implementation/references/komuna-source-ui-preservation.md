# Komuna source-UI preservation and subpath deployment correction

Use this when migrating the cloned `komuna-community-session-bookings` repo to the local Go + SQLite + nginx stack. The cloned repo's `apps/web` frontend is the application/UI source of truth; do not replace it with `komuna-old` or another local-stack frontend just because that donor already builds.

## Correct migration shape

- Preserve the original cloned frontend under `apps/web`.
- Add only deployment/runtime seams needed for the local stack:
  - Vite `base: '/projects/komuna/'` for nginx subpath assets.
  - `BrowserRouter basename={import.meta.env.BASE_URL without trailing slash}` so `/projects/komuna/` maps to the app's `/` route instead of rendering NotFound/blank-looking output.
  - Build with `VITE_API_BASE_URL=/projects/komuna/api/v1` when the local API is mounted at `/projects/komuna/api/v1`.
  - Keep the original app routes/components/i18n/layout unless the user explicitly asks for a redesign.
- Implement local Go/SQLite compatibility endpoints that satisfy the original frontend contract instead of simplifying the frontend to fit the backend. At minimum for public discovery:
  - `GET /api/v1/programs?page=1&limit=100` returns `{ data: ProgramListDTO[], meta: { page, limit, total, total_pages } }`.
  - `GET /api/v1/notifications` and `/api/v1/notifications/unread-count` should return safe defaults if notification UI is mounted.
- If Neon Auth is not configured, add a safe no-auth fallback for public browsing rather than letting the app call `/api/auth/get-session` at the web root and silently fail. The fallback should return `{ data: null, isPending: false, error: null }` for `useSession()` and `null` for token lookup.
- Serve original public assets referenced with absolute paths. Example: the cloned frontend references `/komuna-logo.svg`; either rewrite to `import.meta.env.BASE_URL` or add an nginx/root asset mapping so the header does not show a broken logo.

## Verification checklist

1. Production build from the original frontend directory:
   - `cd apps/web && VITE_API_BASE_URL=/projects/komuna/api/v1 npm run build`
2. Deploy `apps/web/dist` to `/var/www/html/projects/komuna/`.
3. Curl public/index and referenced assets:
   - `curl -fsSI http://<public-ip>/projects/komuna/`
   - parse the JS/CSS asset URLs from the index and verify each returns 2xx.
4. Use a real browser or headless Chromium, not just curl, because React Router/auth/runtime errors can produce a 200 response with blank or wrong UI:
   - Check the DOM contains original-source markers such as `Pesan pertemuan`, `Program tersedia`, `discovery-programs`, and real program names.
   - Check it does not contain `Halaman tidak ditemukan`, `Gagal memuat program`, or donor-project strings like `komuna-old`.
   - Run a mobile viewport/user-agent pass if the user reports a phone blank page.
5. Inspect nginx access logs for the user's browser requests when they still report blankness:
   - Verify it fetched the current hashed JS/CSS bundle, not an older cached asset.
   - Look for 404s such as `/api/auth/get-session`, `/api/v1/programs`, `/komuna-logo.svg`, or missing subpath assets.
6. If stale client caching is suspected, add `Cache-Control: no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0` for the project index during active migration/debugging.

## Pitfalls

- A passing Go test and Vite build does not prove the migrated app is visually/source-correct. Verify the live DOM/screenshot against the original app markers.
- Do not add a hand-written fallback page and mistake it for the migrated app. Fallback content can prevent a completely blank page, but the final check must prove the React app replaced it.
- When a user says "it does not look like the original app," audit for donor frontend files first. Remove copied donor frontend directories and redeploy from `apps/web`.
- If the app is mounted under `/projects/komuna/`, missing React Router `basename` often appears as a blank or not-found page even though assets load with HTTP 200.
- Absolute public asset paths from the original repo may bypass the `/projects/komuna/` alias; map or rewrite them before claiming the UI is fully deployed.
