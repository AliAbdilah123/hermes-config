# Komuna program discovery: urgency sessions, slugs, categories, GPS

Use when updating Komuna's local Go+SQLite/JSON-state deployment around public program discovery or program detail/session UX.

## Durable findings

- The live local API path can be the Go JSON-state server at `api/v1/main.go`, not the old Hono/Drizzle implementation. Inspect service/nginx first; do not assume `apps/api` is live.
- In the Go API, `Program` data is stored inside the JSON `app_state` payload and `programDTO` is the compatibility boundary for frontend DTO fields.
- Existing public program routes may use IDs like `prog-box`; adding human-readable links can be done by returning a derived `slug` while keeping `State.prog()` accepting both `ID` and slug.
- Preserve old UUID/ID links as fallback. Public cards can navigate with `program.slug ?? program.id`, while join/auth redirects should use the same detail path.
- Category may exist only as a single legacy `category`; if the user asks for categories per program, return a `categories: string[]` field while keeping `category` for old UI/tests. For minimal compatibility, derive `categories` from `Category` when no array exists.
- Discovery filters should check both `p.category === activeCategory` and `p.categories?.includes(activeCategory)`.
- For browser location defaults, use native `navigator.geolocation.getCurrentPosition` with `{ enableHighAccuracy:false, timeout:8000, maximumAge:300000 }`; on success set the existing location filter only if still `all`, and on denial/unsupported do nothing so discovery stays usable.
- Do not claim true “closest first” unless the backend has real coordinates/distance sorting. GPS permission alone is not proximity search.
- Session urgency UX can stay frontend-only: compute minutes until `session.startTime`, treat `0 < minutes < 60` as starting soon, and style time/countdown with subtle warm-yellow glow. Pass a `heroPrimary` prop from the first hero session so only the first upcoming card gets stronger emphasis.
- Update both English and Indonesian i18n when adding session countdown copy.

## Verification pattern

- `cd api/v1 && go test ./...`
- `cd apps/web && npm run build`
- Run targeted Vitest files for touched pages/components.
- Deploy Go binary to the service artifact path, restart the Komuna service, copy Vite `dist` to the nginx project alias.
- Verify public API returns `slug` and `categories`, and that both ID and slug program detail endpoints return 200.
- Verify deployed JS contains markers for new UX strings/features when index HTML is only a shell.
