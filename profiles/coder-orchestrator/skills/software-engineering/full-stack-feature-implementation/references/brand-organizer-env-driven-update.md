# Brand Organizer env-driven update example

Session pattern: user asked to update an existing `brand-organizer` project with real implementations after providing env values.

Useful takeaways:

- The repo was a React/Vite frontend plus Go `net/http` + SQLite backend.
- `.env.example` documented integration keys, but runtime code needed to actually consume project-root `.env` values.
- Avoid reading secret env files directly. Inspect `.env.example` and config code instead.
- A safe fix was to:
  - Load root `.env` at Go backend startup before reading `DATABASE_PATH`, `MEDIA_DIR`, payment, and Instagram config.
  - Load root `.env` in the dev orchestrator script before spawning backend/frontend.
  - Support both `VITE_API_URL` and `VITE_API_BASE_URL` in the frontend API base helper, because examples and user-provided env names may differ.
- Verification used:
  - `corepack pnpm --filter frontend typecheck`
  - `corepack pnpm --filter frontend build`
  - `cd apps/backend-go && go test ./... && go build ./...`
- When `pnpm` was not on PATH, `corepack pnpm` worked. Treat this as a retry tactic, not as a durable environment limitation.
- Deployment/restart of the live `brand-organizer.service` required elevated/destructive action and was blocked by the environment, so final reporting distinguished local verified implementation from production deployment.

Recommended final report shape:

```text
Implemented in <repo path>.
Changed files:
- ...

Verification:
- frontend typecheck: passed
- frontend build: passed
- backend tests: passed
- backend build: passed

Blocked/not done:
- live service deploy/restart was not performed because ...
```
