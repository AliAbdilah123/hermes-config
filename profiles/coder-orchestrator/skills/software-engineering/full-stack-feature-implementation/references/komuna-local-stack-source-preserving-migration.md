# Komuna migration implementation notes: local auth fallback and public DOM verification

Use this when migrating the cloned Komuna Hono/Neon/Vite app to a local Go + SQLite + nginx stack under `/projects/komuna` while preserving `apps/web` as the UI source of truth.

## Decisions to encode before implementing

When the user answers plan questions, update the plan and public review HTML before executing. In this session the durable decision pattern was:

- Public path: `/projects/komuna`.
- Git: preserve the cloned repo locally; no push needed unless asked.
- Auth: fully replace Neon Auth in the runtime path, but keep original env key names as compatibility placeholders.
- Payments: Xendit testing mode only; avoid live invoice/charge smoke tests.

## Frontend pitfalls

- Do not instantiate `createInternalNeonAuth()` with a relative placeholder such as `/api/auth`; Better Auth throws `Invalid base URL` before the app renders. If Neon is fully replaced or unset, export a local auth client fallback instead of constructing the Neon client.
- If components call `authClient.useSession()`, the fallback should return a settled unauthenticated state such as `{ data: null, isPending: false, error: null }` so public discovery pages can render.
- Remove or bypass `NeonAuthUIProvider` when Neon is not configured; type-compatible fake adapters can fail at build time.
- For `/projects/komuna/` deployment, set both Vite `base` and React Router `basename`, and default `VITE_API_BASE_URL` to `/projects/komuna/api/v1` when the local API is mounted there.
- If headless/public browser testing on plain HTTP raises `crypto.randomUUID is not a function`, add a small `globalThis.crypto.randomUUID` polyfill loaded before React app initialization. Verify after rebuilding, not just by curl.

## Backend/deployment pattern

- Add the local API as an additive directory in the cloned repo (for example `api/v1`) instead of replacing the original `apps/api` source during early migration.
- Accept original env naming aliases in the local API: `ADDR`, `DATABASE_URL=file:...`, `DATABASE_PATH`, `CORS_ORIGINS`, `XENDIT_SECRET_KEY`, `XENDIT_WEBHOOK_TOKEN`, etc.
- For systemd, use `EnvironmentFile=<project-root>/.env` and never copy/print secret values into the unit or final report.
- Nginx API proxy must match the backend base path. If the Go API serves `/api/v1/*`, then `/projects/komuna/api/v1/*` should proxy to `http://127.0.0.1:<port>/api/v1/*`.

## Verification checklist

- `go test ./...` and `go build` from the local API directory.
- Production frontend build with `VITE_API_BASE_URL=/projects/komuna/api/v1`.
- Install static assets and verify public index plus referenced JS/CSS assets return 2xx.
- Verify `systemctl show <service> -p EnvironmentFiles -p ActiveState -p SubState -p WorkingDirectory` without printing env values.
- Curl public API health and `programs` endpoint.
- Use headless Chromium DOM verification, not only curl 200. Confirm source UI markers such as `Program tersedia`, `Jakarta Fight Club`, and `Bali Sunrise Yoga`; confirm absence of `Halaman tidak ditemukan`, `Gagal memuat program`, and donor strings such as `komuna-old`.
