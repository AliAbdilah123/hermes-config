# Komuna cloned-project isolated local-stack migration notes

Use this when the user asks to clone a fresh Komuna upstream repo and migrate it to the local Go + SQLite + Vite stack without disturbing `komuna-old` or other deployed projects.

## Pattern

1. Clone into the requested project directory and verify `git status --short --branch` plus `git remote -v`.
2. Read project guidance (`AGENTS.md`, `CLAUDE.md`, docs) before editing. Preserve the cloned repo as the source of truth; port only local-stack runtime seams, not unrelated old-project git state.
3. Bring over/adapt the established local-stack directories only:
   - `api/` Go API
   - `frontend/` Vite app
   - root `.env.example`
   - deployment/runbook docs
   Exclude generated/runtime artifacts (`node_modules`, `dist`, API binaries, sqlite files, `api/data`).
4. Rename all project identifiers and public-path defaults from the donor/local-stack project to the requested clone name (`komuna`, not `komuna-old`): service name, Go module, Vite base, frontend session-storage key, UI copy, nginx path, runbook examples.
5. Generate a root `.env` with original/local-compatible env key names and do not print values:
   - `ADDR` on an unused port
   - `DATABASE_PATH=sqlite.db`
   - `CORS_ORIGINS`
   - `KOMUNA_ADMIN_TOKEN`
   - `VITE_API_BASE_URL`
   - reserved integration keys such as `XENDIT_SECRET_KEY`, `XENDIT_WEBHOOK_TOKEN`, `RESEND_API_KEY`
6. Add `.gitignore` entries for `.env`, `.env.*` with `!.env.example`, `sqlite.db*`, API binaries, frontend `node_modules/`, and frontend `dist/`.
7. Deploy isolated runtime only after build/test pass:
   - copy `frontend/dist/` to `/var/www/html/projects/<name>/`
   - create a distinct systemd unit (`<name>-api.service`) with `EnvironmentFile=<project-root>/.env`
   - add an nginx path-specific API proxy before generic `/projects/` handling
   - keep old services/routes untouched.

## Env alias precedence pitfall

If the app loads project-root `.env` and accepts alias names (for example `KOMUNA_ADMIN_TOKEN` preferred, `ADMIN_TOKEN` alias), tests or service overrides may set only the alias. A generated `.env` containing the preferred key can accidentally shadow the explicit alias if `firstEnv("KOMUNA_ADMIN_TOKEN", "ADMIN_TOKEN")` is used after `.env` loading.

Fix by making explicit process overrides win for aliases that tests/operators may set, or by ensuring the dotenv loader never masks values already present before loading. Add/keep a test for alias precedence.

## Verification checklist

- `go test ./...`
- `go build -o server .`
- `npm ci`
- `npm run lint`
- `npm run build`
- `systemctl show <name>-api.service -p EnvironmentFiles -p ActiveState -p SubState -p WorkingDirectory --no-pager`
- `curl -fsS http://127.0.0.1:<port>/api/v1/health`
- `curl -fsS http://127.0.0.1:<port>/api/v1/readyz`
- `curl -fsS http://127.0.0.1:<public-path>/api/v1/bootstrap` and parse a non-empty expected field
- Fetch the public index and each referenced JS/CSS asset, confirming 2xx responses.

## Reporting

Report changed paths, verification commands with pass/fail outcomes, service/path isolation, and the public URL. Do not reveal `.env` values; at most report key names or value lengths.