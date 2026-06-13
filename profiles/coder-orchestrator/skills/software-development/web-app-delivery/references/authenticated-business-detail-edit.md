# Authenticated business detail edit pattern

Use when an existing CRM/local-business app needs an "edit details" flow for records already shown in a read-only modal/table.

## Implementation pattern

- Keep the existing stack and data model stable; add a narrow update path instead of rebuilding the CRUD surface.
- Backend:
  - Add an authenticated + CSRF-protected `PATCH /api/v1/businesses/{id}` route beside the existing detail route.
  - Decode the same business DTO used by list/detail endpoints so the response shape remains consistent.
  - Validate required identity fields (`name`, `category`, `city` for this app class) and return `422` for missing required values.
  - Update all editable columns plus `updated_at`, then re-read the row and return `{ "business": ... }`.
  - Add a persistence test: login/session where needed, patch a record, then GET it again and assert changed fields persisted.
- Frontend:
  - Add an `onSave` callback at the app/page owner where the authoritative list state lives.
  - In the read-only detail modal, add an `Edit Detail` action that swaps to an inline form/modal rather than creating a disconnected page.
  - Submit with `PATCH /businesses/{id}` and the existing CSRF token; update both the list row and currently open detail modal from the API response.
  - Keep labels and notices in the product language (Bahasa Indonesia for Indonesia-local-business apps).

## Verification

Minimum checks before reporting done:

```bash
go test ./...
npm run build
```

If the app is deployed under systemd/nginx, rebuild and install the backend binary, deploy the new `dist/`, restart the service, and verify:

```bash
systemctl is-active <service>
curl -i http://127.0.0.1:<port>/healthz
curl -I http://127.0.0.1/projects/<project>/
```

For authenticated mutation smoke checks, use a cookie jar and extract the CSRF token from login, then call the mutation and assert the returned changed field:

```bash
jar=$(mktemp)
login=$(curl -sS -c "$jar" -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"..."}' \
  http://127.0.0.1:<port>/api/v1/auth/login)
csrf=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["csrfToken"])' <<<"$login")
# GET a record, PATCH with X-CSRF-Token, then assert returned/persisted fields.
```

Do not stop at a successful build when the user asked to add the feature to a live project; deploy and exercise the mutation through the real authenticated API.