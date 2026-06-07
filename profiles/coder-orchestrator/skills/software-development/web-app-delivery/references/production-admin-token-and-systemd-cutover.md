# Production admin-token gate + systemd cutover notes

Use this when hardening a single-user/internal web app that is publicly reachable but should not expose mutable operations to anyone on the internet.

## Admin token pattern for public single-user apps

- Keep safe read endpoints public when useful (`GET /health`, `GET /posts`, `GET /stats`).
- Require an admin token for all mutating methods (`POST`, `PUT`, `PATCH`, `DELETE`) when the deployment sets `ADMIN_TOKEN`.
- Accept both:
  - `X-Admin-Token: <token>`
  - `Authorization: Bearer <token>`
- Return a JSON `401` response for missing/wrong tokens.
- Keep development ergonomic by allowing mutations when `ADMIN_TOKEN` is unset, but set it in production systemd/env.
- Frontend UX should include a small password/token control persisted in `localStorage` and attach the token only to mutating API calls. GET calls should continue to work without a token.
- Tests should cover: public GET succeeds; unauthenticated mutation returns `401`; wrong token returns `401`; valid header allows create/update/delete/duplicate/publish-like actions.

## Systemd cutover pattern

When replacing a previously agent-started/background backend with systemd:

1. Build/install the new binary first.
2. Check the target port with `ss -tlnp | grep :<port>`.
3. If an old manual/background process owns the port, stop/kill it before starting systemd.
4. `systemctl daemon-reload && systemctl restart <service>`.
5. Verify with `systemctl status`, direct backend curl, and nginx curl.

A service that immediately fails with `listen tcp 127.0.0.1:<port>: bind: address already in use` usually means the old process is still serving stale code, so nginx smoke tests may appear to hit the app while systemd is actually failed.

## Repo cleanliness

Do not track generated backend binaries or local SQLite DBs. Add patterns such as:

```gitignore
backend/bin/
backend/*.db
frontend/dist/
```

Before final handoff, verify `git status --short` is clean after builds/deploys.