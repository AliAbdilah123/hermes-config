# Komuna source-of-truth and visual parity correction

Use this when migrating Komuna from the original Cloudflare/Neon/Vercel stack to a local Go + SQLite + Vite deployment and the user reports that the result does not look like the original cloned app.

## Lesson

A successful build/deploy is not enough. For Komuna, the cloned repo's `apps/web` is the UI source of truth. Do **not** replace it with a simplified donor UI from `komuna-old` or any boilerplate just because that donor already has a local Go/SQLite stack. Port only runtime seams, backend compatibility endpoints, and deployment config.

## Corrective workflow

1. **Restore source UI**
   - Keep `apps/web` as the deployed frontend. Remove any copied donor `frontend/` tree unless the user explicitly requested a redesign.
   - Set Vite `base` for the deployment path (for example `/projects/komuna/`).
   - Set React Router `BrowserRouter basename` from `import.meta.env.BASE_URL` so `/projects/komuna/` routes to the app root rather than NotFound/blank.

2. **Match original runtime state before judging visual parity**
   - Compare against the user-provided/original URL screenshot, not against a desktop local default.
   - If the original screenshot is dark/logged-in, ensure the local deployment has equivalent runtime state:
     - default dark theme when no explicit stored theme exists;
     - safe demo auth/session fallback only when real auth env is absent;
     - local `/api/v1/me/workspace` so dashboard/nav/profile/notification UI appears.
   - Preserve original language defaults (`id` for Indonesian Komuna pages) and original translation strings.

3. **Avoid blank-page regressions**
   - If using a subpath deployment, verify rendered DOM with mobile viewport/user agent and check for the original app markers (`Pesan pertemuan`, `Program tersedia`, app cards), not only 200 responses.
   - Add no-cache headers for the project index while iterating so phones do not keep stale blank JS/HTML.
   - It is okay to include minimal visible fallback content inside `#root` for no-JS/failed-JS safety, but verify it disappears after React mounts; if the user says it looks unlike the original, remove or minimize fallback styling influence.

4. **Backend compatibility for the original UI**
   - Implement only the local API endpoints needed by the original frontend paths first, e.g. `/api/v1/programs`, `/api/v1/me/workspace`, notifications/unread counts.
   - Shape responses to the frontend DTOs (`ProgramListDTO`, `WorkspaceSummaryDTO`) rather than returning the donor/simple app's data model.
   - Expect remaining differences to come from local demo data vs original Vercel/Neon data; call this out honestly and then seed/map data for parity if requested.

## Verification checklist

- `go test ./...` and `go build` for the local API.
- `VITE_API_BASE_URL=/projects/komuna/api/v1 npm run build` for `apps/web`.
- Curl public index and asset URLs for 200.
- Headless/mobile DOM contains original markers and does **not** contain NotFound/error markers:
  - contains: `Pesan pertemuan`, `Program tersedia`, `Dasbor` when matching logged-in screenshot, known program names.
  - absent: `Halaman tidak ditemukan`, `Gagal memuat program`.
- Check nginx access logs for missing absolute assets such as `/komuna-logo.svg`; copy/alias public assets when original source uses root-absolute paths.

## Pitfalls

- Do not claim "matches original" after only checking desktop or local 127.0.0.1. The user's comparison may be mobile Chrome against the Vercel app.
- Do not hide a blank page with a fallback and then treat the fallback as success; verify the React app replaced it.
- A logged-out local app may be technically working but visually different from the user's logged-in original screenshot.
