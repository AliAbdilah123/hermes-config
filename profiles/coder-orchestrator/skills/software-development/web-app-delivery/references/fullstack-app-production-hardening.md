# Production hardening checklist for small React + Go + SQLite apps

Use this when the user asks to refine a delivered app until it is "production grade" or similar.

## Backend hardening
- Make app/handler construction testable instead of only wiring handlers in `main()`.
- Return consistent JSON error envelopes, including status/code/message.
- Enforce HTTP methods and set `Allow` headers for rejected methods.
- Set request body size limits before JSON decoding.
- Add security headers at the API layer when nginx may proxy errors/responses: `Content-Security-Policy`, `Referrer-Policy`, `X-Content-Type-Options`, `X-Frame-Options`.
- Add server timeouts: read, write, idle, and header timeouts.
- Add `/readyz` or equivalent readiness endpoint.
- Do not bind public-facing app backends on `0.0.0.0` when nginx is the public entrypoint; bind `127.0.0.1:<project-port>`.
- Make port, DB path, CORS allowlist, and admin token configurable via environment.
- Protect mutation/admin endpoints. For small internal apps, a shared admin token is acceptable only as an interim gate; real auth/roles remains follow-up work.

## SQLite hardening
- Store runtime DB outside the repo, commonly `/var/lib/<project>/<project>.db`.
- Ensure service user owns the DB directory.
- Enable WAL and a busy timeout.
- Use transactions for multi-step mutations.
- Add schema initialization and tests around mutation behavior.

## Frontend hardening
- Add loading, error, and empty states for every API-dependent view.
- Disable mutation buttons while requests are in flight.
- Expose a clear way to provide an admin token if mutations require one.
- Keep focus states, labels, and contrast accessible.
- Re-run visual screenshot smoke after layout/CSS changes; builds and curls do not catch overlap/clipping.

## Deployment hardening
- Run the Go API as a systemd service with an env file such as `/etc/<project>/<project>.env`.
- Keep secrets out of chat and repo. Tell the user where to retrieve them locally instead of printing them.
- Rebuild frontend, copy `frontend/dist` to the nginx-served project path, and reload nginx only after `nginx -t` passes.
- Verify service status, readiness endpoint, auth rejection for unauthenticated mutation, authenticated mutation success, and localhost-only backend binding before reporting done.
- Add or update a deployment runbook with service names, env vars, DB path, backup/restore, and known follow-ups.

## Report shape
Keep the final response concise: commit hash, public URL, exact verification commands/results, and remaining external choices such as domain/HTTPS, real auth, and data-model/migration maturity.