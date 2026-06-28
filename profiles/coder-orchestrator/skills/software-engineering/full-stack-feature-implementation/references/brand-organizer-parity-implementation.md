# Brand Organizer parity implementation notes (upstream TS/Cloudflare -> Go/SQLite)

Use after a parity audit identifies upstream UI/backend gaps that must be implemented in the migrated React/Vite + Go/SQLite stack without reverting to the upstream Worker/Neon architecture.

## Durable implementation pattern

1. **Add parity tests before filling gaps**
   - Backend: add Go tests for route presence and response shape, especially when implementing upstream Worker routes as local Go equivalents.
   - Frontend: add focused tests for user-visible parity, not exact upstream internals (e.g. forgot-password link, social auth buttons, theme toggle presence).
   - Run the targeted failing tests first to confirm the gap is real, then implement.

2. **Translate upstream frontend features without importing incompatible auth stack**
   - Shared auth UI components (`AuthBranding`, `AuthDivider`, social icons/buttons, password visibility) can be copied/adapted directly.
   - Forgot-password route can be added while preserving local Go auth; point it at a Go endpoint that returns non-enumerating success.
   - Keep local `authClient` email sign-in/sign-up when the deployed stack uses Go sessions. Do not blindly switch to Neon Auth unless the stack is being migrated back to Neon.
   - For Google/Instagram social actions, surface the UI affordance but preserve stable local behavior: Google can show a clear not-configured message; Instagram can route to the existing Go connect/start path.
   - PostHog parity can be represented by a typed event taxonomy/shim when avoiding a new external dependency; use a no-op-safe `track()` wrapper.

3. **Translate upstream backend route parity into local handlers**
   - Add Worker route aliases to Go dispatch when frontend/upstream expects them, e.g. `/api/facebook/oauth/start` and `/api/facebook/oauth/callback` can delegate to the existing Facebook/Instagram OAuth implementation.
   - For feature areas that depend on external Graph/R2/queues in upstream, implement honest local equivalents with real persistence/response shapes rather than stubs:
     - hashtags: searchable/suggested/history endpoints backed by SQLite history plus deterministic local result generation when Graph credentials are absent.
     - comments: SQLite-backed list/create endpoints.
     - sync: update local analytics counters and return `synced`/timestamp.
     - Xendit webhooks: persist raw event metadata in SQLite and acknowledge.
     - queue/enqueue hook: transition due local posts and return enqueue count.
   - Keep degraded/mock paths explicit and safe; do not claim real external publishing/sync if credentials and background services are not wired.

4. **Schema additions for local parity**
   - Add small SQLite tables for new persisted behaviors rather than overloading existing rows:
     - `hashtag_history(id,user_id,query,result_count,created_at)`
     - `instagram_comments(id,user_id,media_id,message,username,created_at)`
     - `webhook_events(id,provider,event_type,external_id,payload,created_at)`
   - Keep migrations idempotent inside the Go `migrate()` flow for this project’s current simple SQLite migration style.

5. **Verification and deployment**
   - Run full verification: frontend typecheck, frontend tests, frontend build, backend tests, backend build.
   - If deploying locally on this host, build backend from `apps/backend-go`, install the binary, rsync frontend `dist/`, restart `brand-organizer.service`, then verify live health and at least one newly added endpoint.
   - Pitfall: after `cd apps/backend-go`, relative frontend paths like `apps/frontend/dist` resolve incorrectly. Use absolute repo paths for deployment copy steps or return to repo root first.

## Reporting

Report implemented parity by category (frontend/UI, backend/API, tests, deployment), exact verification commands, live smoke checks, and the public project URL. Clearly label any parity that remains intentionally local/degraded because it depends on external services (Neon Auth, PostHog ingestion, Meta Graph, queues, R2, mailer).