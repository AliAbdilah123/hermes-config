# PRD gap completion in a Go + SQLite + Vite app

Use when a user asks to implement the remaining points from a previously audited PRD in a small single-file Go API + Vite app.

## Pattern

1. Convert PRD gaps into thin vertical slices, not a huge rewrite:
   - DB table(s) for durable state.
   - Authenticated route(s) for create/list/run actions.
   - One native frontend control/page/button that exercises the route.
   - Smoke test the route through login/CSRF if the app uses sessions.
2. For late-stage PRD features, prefer deterministic/manual-first behavior:
   - Enrichment: store suggestions in `enrichment_runs`; do not overwrite core business fields silently.
   - Website audit: safe timeout HTTP check + stable `checks_json`; missing website is a completed audit with a landing-page offer.
   - AI enrichment: if no approved provider/API key flow exists, use an explicit deterministic fallback and mark it clearly (`provider: deterministic-fallback`) rather than inventing external AI behavior.
   - Campaigns: preview first, persist confirmation token/campaign id, confirm before queueing messages.
   - Automation: manual-run job endpoints first; scheduler/ticker later only after manual runs are stable.
   - Reports/geo: compute JSON metrics first; HTML/CSV exports/map visualizations later.
3. Frontend scope should be minimal but real:
   - Add nav/page for jobs and reports.
   - Add business-detail buttons for enrichment/audit/AI suggestions.
   - Display returned JSON/summaries; avoid large custom state machines.
4. Verification sequence:
   - `gofmt -w cmd/api/main.go`
   - `go test ./...`
   - `npm run build`
   - `go build -o bin/<app> ./cmd/api`
   - Deploy static `dist/` to the nginx-served project directory.
   - If copying the running Go binary fails with `Text file busy`, stop the systemd service, copy the binary, then start it again.
   - Smoke `healthz`, public SPA asset markers, and at least one authenticated API path (login -> create job -> run job -> list runs/reports).

## Pitfalls

- Do not claim full external AI/provider implementation if the durable work is a deterministic fallback. Name the skipped provider wiring and when to add it.
- Do not skip authenticated smoke tests for features hidden behind session/CSRF; public `healthz` does not prove the new workflow works.
- When a repo has unrelated pre-existing dirty files, stage only the files touched for this task and report push blockers separately.
