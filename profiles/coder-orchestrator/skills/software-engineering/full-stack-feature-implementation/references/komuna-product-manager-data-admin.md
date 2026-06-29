# Komuna product-scoped manager data admin

Use when the user asks to make an existing email a manager for a product in Komuna's local Go + SQLite JSON-state deployment.

## Data shape

Komuna's deployed local API stores domain state in SQLite table `app_state(id=1, payload JSON)`, while auth users/sessions are in SQL tables:

- `auth_users(id, email, name, password_hash, created_at)`
- `auth_sessions(token, user_id, ...)`
- JSON state collections use capitalized keys: `Programs`, `Products`, `Members`, `Audit`, etc.
- Product-scoped manager role shape inside a member is:

```json
{"role":"manager","product_id":"prod-box"}
```

A member assignment should point at the same `UserID` as the row in `auth_users` when the email already exists. If no auth user exists, create only the membership if that is acceptable for the request; otherwise ask whether to create an account/sign-up flow.

## Workflow

1. Safely read `SQLITE_DB_PATH` from the project `.env` without printing secrets.
2. Load `app_state.payload` and list matching `Programs` and `Products` when the product is ambiguous.
3. Ask the user to choose if the target program has multiple active products.
4. Before editing, copy the SQLite DB to a timestamped backup path next to the DB.
5. Find the `auth_users` row by case-insensitive email. Use its `id` and `name` for the member when present.
6. Find or create a `Members` entry for the target `ProgramID` + email:
   - `Status: "active"`
   - `UserID` equals the auth user id when present
   - append `{ "role": "manager", "product_id": <target product id> }` only if not already present
7. Add a concise audit entry to `Audit` with the email, role, product id/name, and timestamp.
8. Write the updated JSON back to `app_state` and commit.

## Verification

- Query the DB and assert:
  - `auth_users.id == Members[].UserID` for the email when an auth user exists
  - the member has `Status == "active"`
  - the member has exactly the requested product-scoped manager role
- Public API smoke can use `X-Komuna-User: <user_id>` against `/projects/komuna/api/v1/me/workspace` to verify the workspace response includes:
  - `isSuperAdmin: false`
  - `programName: Jakarta Fight Club` (or target program)
  - role `{ "role": "manager", "product_id": <product id> }`
- If using a real bearer session for the target email, first check that an `auth_sessions` row exists; otherwise DB-level verification plus the dev-user header smoke is sufficient.

## Pitfalls

- Do not assign a program-level manager role with `product_id: null` when the user asked for manager of a product.
- Do not guess which product if a program has multiple active products; ask the user.
- Do not print `.env` contents or secrets while locating the database.
- Host-root `/api/v1` may 404 publicly for Komuna; use `/projects/komuna/api/v1` through nginx.
