# Local Go + Vite env refresh and smoke verification

Use this when a user says they updated `.env` and asks to refresh/restart a deployed local app (Go API + Vite SPA behind nginx/systemd).

## Safe refresh sequence

1. Treat `.env` values as secret: inspect only key names if needed, never print values.
2. Verify the systemd unit uses `EnvironmentFile=/path/to/project/.env` rather than copied secret values.
3. **Determine if a rebuild is needed:**
   - **Env-only change** (user updated values in `.env`, no code changed): skip rebuild. Go straight to step 4 — systemd re-reads the `EnvironmentFile` on restart, so the new env values are picked up by the existing binary.
   - **Code change**: rebuild backend and frontend before restart:
     - Backend: run the project-native build/test command, e.g. `go test ./... && go build -o ../server .` from the Go module directory.
     - Frontend: run the project-native build, e.g. `npm run build` from the Vite app directory.
4. Restart the systemd service so the new process picks up the updated env (and rebuilt binary if applicable).
5. Sync frontend `dist/` to the nginx-served directory only after a successful build.
6. Verify public index and referenced JS/CSS assets return 2xx.
7. Verify API health and a few feature endpoints through the public route, not only localhost.
8. Use headless Chromium `--dump-dom` as a lightweight browser smoke test when interactive browser tooling is slow or unavailable; check for real app text/DOM markers, not just the static HTML title.

## Feature smoke patterns

- API health: public `/api/v1/health` returns 200 JSON.
- List/data endpoint: public programs/list endpoint returns expected data shape and at least one known record.
- Env-sensitive integration endpoint: exercise the non-destructive quote/config path rather than creating live charges/invoices.
- Auth/session if recently touched: create a throwaway user, sign in, fetch session, sign out; do not log tokens.
- For checkout quote endpoints, test both a known-good package id and a bad package id. A bad id should return a controlled 4xx JSON error, never panic/502.

## Pitfalls

- A service can remain `active (running)` even while individual HTTP handlers panic. Always smoke the feature endpoints after restart and inspect recent journal logs for new `panic`/`error` lines.
- Avoid writing invalid test tokens or secret values into shell output. Mask bearer tokens in commands/logs.
- Full frontend test suites may have pre-existing failures unrelated to an env refresh. Report them honestly, but do not treat them as proof that deployment failed if production build and live smoke checks pass.
- **Port conflict crash-loop after env update**: If the service enters `activating (auto-restart)` with exit-code 1, check `journalctl -u <service> -n 30` for `bind: address already in use`. Another service on the same host may occupy the default port (e.g. `fnb-pos-server` on 8080). Use `ss -tlnp | grep <port>` to identify the occupant. The fix is to set the correct port env var in `.env` so the service listens on the port nginx expects (check `proxy_pass` in the active nginx config), not to kill the other service.
- **Go binary env var name for port may not be `PORT`**: Go APIs often use a non-standard env var for the listen address. SocialZen uses `ADDR` (from `models.Env("ADDR", ":8080")` in `main.go`), defaulting to `:8080`. Always grep the Go source for `ListenAndServe` or `Env("` to find the actual env var name before adding it to `.env`. Setting `PORT=8089` when the binary reads `ADDR` silently does nothing — the service keeps crashing on the default port.
