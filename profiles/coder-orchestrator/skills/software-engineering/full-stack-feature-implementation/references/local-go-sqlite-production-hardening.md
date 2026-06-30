# Local Go + SQLite Production Hardening

Use this reference when a local Go + SQLite API that started as a demo/local-parity backend (JSON-state-in-SQLite, demo-user fallback, permissive CORS) needs to be made production-ready without a full rewrite to Postgres/cloud auth.

## When to apply

- The user asks to "make this app production-ready" after a local Go+SQLite migration.
- The Go API has unauthenticated demo-user fallbacks, `*` CORS, `http.Error` plain-text errors, no body limits, no validation, and no SQLite pragmas.
- The frontend already builds and the API surface is already compatible — the gap is safety/reliability, not features.

## Hardening checklist (smallest safe diff)

### 1. Auth gate in the CORS/middleware wrapper

Add a single auth check in the `withCORS` (or equivalent) wrapper so every `/api/*` route except public paths rejects requests with no bearer token:

```go
if strings.HasPrefix(r.URL.Path, "/api/") && !isPublicAPI(r.URL.Path) && bearerToken(r) == "" {
    jsonError(w, http.StatusUnauthorized, "unauthorized")
    return
}
```

Public paths: `/api/healthz` and `/api/auth/*`. Everything else (users, goals, tasks, energy, habits, focus, task-groups) requires a valid session token.

Also remove any demo-user fallback in `handleUsers` or `userIDForRequest` — if `userFromRequest` fails, return 401, not a demo user.

### 2. JSON error responses

Replace all `http.Error(w, "...", status)` with a `jsonError` helper that sets `Content-Type: application/json`, calls `WriteHeader`, and encodes `{"error": msg}`. This includes `respond`, `method`, `notFound`, and auth handler error paths.

### 3. Request body limit

In the `decode` helper, wrap the body reader with `io.LimitReader(r.Body, 1<<20)` (1 MB). This prevents oversized JSON payloads from consuming server memory.

### 4. Security headers

In the CORS wrapper, add:
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: same-origin`
- Configurable CORS origin via env (`SELF_FLOW_CORS_ORIGIN` or similar) instead of hardcoded `*`.

### 5. SQLite pragmas

At store initialization, execute these pragmas before the schema `CREATE TABLE`:
```sql
pragma journal_mode=WAL
pragma busy_timeout=5000
```
WAL mode improves concurrency and crash safety; `busy_timeout` prevents `SQLITE_BUSY` errors under concurrent access.

### 6. Input validation

Add a `validateItem(name, body, create)` function and call it at every mutation entry point (POST collection, PUT/PATCH by-id, task create/date/bulk-update, goal create):

- **Goals**: category must be one of `Main, Yearly, Quarterly, Monthly, Weekly, Daily`; status must be `active` or `done`.
- **Tasks**: status must be one of `todo, in progress, blocked, completed, not done, delegated, commitment`; priority and effort must be `low, med, high` or null.
- **Energy**: level must be 1-10.
- **Habits/habitLogs**: habitId and optionId required on create.
- **Dates**: any `date` field must parse as `YYYY-MM-DD`.
- **Required titles**: goals, tasks, habits, taskGroups require non-empty `title` on create.

Return controlled `400 {"error": "..."}` for invalid payloads — never let corrupt data enter the JSON state.

### 7. Env example

Add `.env.example` with safe key names only (no values):
- `SELF_FLOW_ADDR`, `SELF_FLOW_DB`, `SELF_FLOW_CORS_ORIGIN`
- `VITE_BASE_PATH`, `VITE_API_URL`

## Verification

After hardening, run these checks:

1. `go test ./...` from `api/v1` — update existing tests to include `Authorization: Bearer <token>` headers (signup a user first via `signupToken` helper).
2. `VITE_BASE_PATH=/projects/<slug>/ VITE_API_URL=/projects/<slug>/api pnpm --filter fe build` — frontend must still build.
3. Restart systemd service, copy static build to nginx-served directory.
4. Public smoke tests:
   - `GET /api/healthz` → 200 `{"ok":true,...}`
   - `GET /api/goals` without token → 401 `{"error":"unauthorized"}`
   - `POST /api/auth/sign-up` → 200 with token
   - `GET /api/goals` with token → 200 `{"data":[]}`
   - `POST /api/energy` with `{"level":99}` → 400 `{"error":"energy level must be between 1 and 10"}`
   - Public SPA index → 200
   - Public JS asset under `/projects/<slug>/assets/` → 200

## Pitfalls

- Existing tests that used unauthenticated requests will fail after adding the auth gate. Patch them to signup first and attach a bearer token — the `signupToken` test helper already exists in most migrated repos.
- `validateItem` should be a no-op (`return nil`) when `b` is nil to avoid panics on empty update bodies.
- Don't forget to add the `io` import when switching to `io.LimitReader`.
- `gofmt -w` the modified files before running tests — Go compiler will reject formatting issues in CI.
- When rebuilding the Go binary, run `go build` from the `api/v1` directory, not the project root (the Go module lives in `api/v1/`).

## What this pass does NOT cover

- Full Postgres/Drizzle migration (JSON-in-SQLite remains).
- Stack Auth restoration (local email/password sessions remain).
- Multi-tenant/org permissions.
- Rate limiting, logging, or observability.
- Automated backups of the SQLite database.

Add those when the app has multiple real users/orgs or needs cloud scale.