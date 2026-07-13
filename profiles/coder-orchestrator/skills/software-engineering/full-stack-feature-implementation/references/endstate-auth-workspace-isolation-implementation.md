# Endstate-style auth + workspace isolation implementation

Use this as a concrete pattern when a small Go + SQLite + React/Vite app has workspace/project tables but no real session boundary.

## Minimal backend slice

- Add `auth_users` and `auth_sessions` in the existing SQLite DB.
- Register `POST /api/auth/signup`, `POST /api/auth/signin`, and `GET /api/auth/me` before protected resource routes.
- Signup transaction should create:
  1. user row with hashed password,
  2. private/default workspace,
  3. `workspace_members` owner row,
  4. session token row.
- Require `Authorization: Bearer <token>` for workspace/project/diagram routes.
- `GET /api/workspaces` must join through `workspace_members` for the session user.
- `POST /api/workspaces` must create workspace + owner membership in one transaction.
- Project/diagram handlers should check `projects.workspace_id -> workspace_members` for the session user before loading or mutating.

## Minimal frontend slice

- Store the returned token in localStorage or the app's existing session store.
- Centralize the API helper so every request includes `Authorization: Bearer ...` when a token exists.
- Gate the app shell behind a compact sign-in/sign-up form; only load workspaces after auth is established.
- Add a sign-out control that clears token and local app state.

## Tests and smoke

- Backend: cover signup/signin, owned workspace creation, and a cross-user workspace/project denial helper or HTTP test.
- Frontend: seed localStorage token in existing app-shell tests, or add a focused auth-screen test.
- Deployment: rebuild backend from the backend module directory if the repo root is not a Go module; then copy only `index.html` and `assets/` for Vite deployments if a root-owned `docs/` directory lives under the public root.
- Public API smoke: create a throwaway signup through the public domain and report only HTTP status / token length / redacted email; never print full bearer tokens.

## Pitfalls

- A pre-existing `workspace_members` table does nothing until every route derives membership from the authenticated session user.
- In tiny apps, a stdlib iterative SHA-256 password hash may satisfy the “no new dependency” rung only as a stopgap; prefer an existing bcrypt/argon2 dependency if already present.
- `curl ... | python3 - <<'PY'` feeds the here-doc to Python stdin, not the curl response. Use `python3 -c '...'` or save the response to a variable/file when parsing public smoke JSON.
