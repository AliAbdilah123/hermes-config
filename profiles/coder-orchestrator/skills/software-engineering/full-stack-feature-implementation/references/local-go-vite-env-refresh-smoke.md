# Local Go + Vite env refresh and smoke verification

Use this when a user says they updated `.env` and asks to refresh/restart a deployed local app (Go API + Vite SPA behind nginx/systemd).

## Safe refresh sequence

1. Treat `.env` values as secret: inspect only key names if needed, never print values.
2. Verify the systemd unit uses `EnvironmentFile=/path/to/project/.env` rather than copied secret values.
3. Rebuild backend and frontend before restart/sync:
   - Backend: run the project-native build/test command, e.g. `go test ./... && go build -o ../server .` from the Go module directory.
   - Frontend: run the project-native build, e.g. `npm run build` from the Vite app directory.
4. Restart the systemd service after the backend artifact is rebuilt so the new process picks up the updated env.
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
