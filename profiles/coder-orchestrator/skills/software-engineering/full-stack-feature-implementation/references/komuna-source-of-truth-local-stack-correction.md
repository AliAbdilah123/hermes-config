# Komuna source-of-truth local-stack correction

Use this when migrating Komuna from the original Hono/Cloudflare/Neon repo to the local Go + SQLite + Vite stack.

## Lesson

The cloned Komuna repo is the source of truth for the application UI. Do not copy the simplified `komuna-old` frontend just because it already has a local Go/SQLite stack. That produces a working app with the wrong product surface and the user will see it as the old project.

## Corrective workflow

1. Preserve `apps/web` from the cloned repo. Remove any donor `frontend/` copied from `komuna-old` or another local project.
2. Keep the local-stack backend isolated in a separate `api/` directory, with project-root `.env` and `sqlite.db`.
3. Add only deployment/runtime seams to the original frontend:
   - Vite `base: '/projects/komuna/'`.
   - `BrowserRouter basename={import.meta.env.BASE_URL...}` so `/projects/komuna/` routes to the app root instead of rendering NotFound/blank-looking output.
   - Build with `VITE_API_BASE_URL=/projects/komuna/api/v1` when deploying under nginx path prefix.
   - If `VITE_NEON_AUTH_URL` is not configured for the local demo, provide a safe no-auth fallback for `authClient.useSession()`/`getJWTToken()` and skip wrapping with `NeonAuthUIProvider`; otherwise the app may keep calling `/api/auth/get-session` and surface blank/error states.
4. Add minimal Go API compatibility endpoints required for the public discovery page before claiming the frontend works:
   - `GET /api/v1/programs` returns `{data, meta}` matching `ProgramListDTO`.
   - `GET /api/v1/notifications` and `/api/v1/notifications/unread-count` can be no-op/demo-compatible if notifications are not central to the smoke path.
5. Rebuild from `apps/web`, deploy `apps/web/dist`, restart the API if changed, and verify through nginx.

## Verification pattern

- `go test ./...` and `go build -o server .` from `api/`.
- `VITE_API_BASE_URL=/projects/komuna/api/v1 npm run build` from `apps/web/`.
- Curl public index, JS, CSS, and `/projects/komuna/api/v1/programs`.
- Use a headless browser DOM dump (or browser QA) to verify rendered app markers, not just HTTP 200:
  - Not present: `Halaman tidak ditemukan`, `Gagal memuat program`, `komuna-old`.
  - Present: `available-programs`, `discovery-programs`, `Jakarta Fight Club`, `Bali Sunrise Yoga`.

## Pitfalls

- A successful Vite build is not enough: React Router without `basename` can still render the app's NotFound page at `/projects/komuna/`.
- HTTP 200 on `index.html` and assets is not enough: auth/session calls or API base mismatches can still leave the user with a blank/error UI.
- Avoid treating upstream lint failures as blockers for this correction if production build succeeds and the lint errors pre-exist in the cloned frontend; report them separately.
