# Boilerplate-to-new-project: Kanban/delegation app implementation pattern

Use this when the user asks to create a new local project from the boilerplate and implement a PRD-backed collaborative/task/kanban app.

## Proven workflow

1. **Seed from boilerplate safely**
   - Copy the boilerplate into the new project directory excluding `.git`, `node_modules`, build output, and live DB files.
   - Keep the copied project identity isolated: update Vite `base` to `/projects/<slug>/`, deployment paths, service name, DB path, and nginx route names.

2. **Create a session kanban board first**
   - Track at least: PRD analysis, seed/copy, plan, implementation, verification/deployment.
   - If using subagents, dispatch them only after the project shell exists; have them inspect backend/frontend separately and return route/test/build details. Keep final integration, deployment, and public verification in the parent agent.

3. **TDD for frontend behavior**
   - Replace boilerplate tests with PRD-facing behavior tests before implementing: public product shell, login-to-workspace, kanban columns, project creation, AI user creation, mentions/subtask conversion, AI queue/forwarder test.
   - Run the native test command. Do not pass Jest-only flags such as `--runInBand` to Vitest.

4. **Local Go + SQLite backend shape**
   - Prefer tenant-scoped endpoints under `/api/v1/tenants/{tenantID}/...` when the boilerplate already has tenants/memberships.
   - For a compact MVP, a single `delegation-workspace` aggregate endpoint can feed the frontend with `projects`, `users`, `delegated_statuses`, `delegated_groups`, `tasks`, `messages`, and `ai_runs`.
   - Add domain tables with a new migration, but handle added columns to existing tables idempotently in Go startup/schema ensure code if the existing migration runner re-runs every `.sql` file without a migration ledger. SQLite `ALTER TABLE ADD COLUMN` is not idempotent.
   - For AI users, keep secrets server-side: store token references/hashes and return only `has_token`/`hasToken`, never the raw token.

5. **Frontend subpath/API pitfalls**
   - For deployed Vite apps under `/projects/<slug>/`, set `base: '/projects/<slug>/'`.
   - Client API helpers should call `/api/...` directly in dev/tests, and project-prefixed API paths in production when the app is served under the subpath. Ensure tests and production behavior agree with nginx proxy paths.
   - If shadcn/Radix dialogs cause test focus/aria-hidden complications for simple auth smoke tests, a plain accessible modal (`role="dialog"`, `aria-modal`, labelled heading) is acceptable for the MVP.
   - Capture form elements before awaits (`const formEl = event.currentTarget`) before calling `reset()`; React synthetic event/currentTarget can be null after async work.
   - When optimistic UI adds partially-shaped records from an API response (for example a converted subtask), normalize defaults before inserting into state so the card actually renders in the expected kanban column.

6. **Deployment verification**
   - Build backend binary, install a project-specific systemd unit, deploy frontend build to `/var/www/html/projects/<slug>/`, add nginx routes before the generic `/projects/` fallback, and reload nginx after `nginx -t` passes.
   - Verify: service active, local health endpoint, public index 200, public JS/CSS asset 200, app-specific marker inside the JS bundle if `index.html` is generic, public API health, authenticated workspace/API smoke.

## Verification commands

```bash
cd backend && go test ./...
cd ../frontend && npm test && npm run build
curl -fsS http://127.0.0.1:<port>/api/v1/health
curl -fsS http://<public-host>/projects/<slug>/
curl -fsS http://<public-host>/projects/<slug>/api/v1/health
```
