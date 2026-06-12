# Full-stack App Authentication Hardening

Use this reference when turning a prototype web app into a production-like app with real authentication and role-aware flows.

## Backend checklist

- Remove prototype identity shortcuts such as `X-User-ID`, `?user_id=`, or hardcoded demo users in API clients.
- Hash passwords before storage. For Go apps, `golang.org/x/crypto/bcrypt` is a straightforward default when dependency policy allows it.
- For existing seeded/demo rows that used plaintext passwords, add a startup migration that hashes any non-hashed values so demo credentials keep working.
- Return opaque random bearer tokens from login. Persist only token hashes in the database, with `user_id`, `expires_at`, and `created_at`.
- Add `POST /auth/logout` to delete the current session and make `GET /me` read from the bearer session.
- Define public endpoints explicitly; everything else should require bearer auth. Typical public endpoints: health, read-only marketplace browsing, register/login, and verified external webhooks.
- Enforce role checks at route boundaries: admin routes require admin, provider actions require provider, customer actions require customer.

## Participant authorization pitfall

Role checks are necessary but not sufficient. After adding roles, verify object-level authorization for every mutation:

- Customer job actions (`pay`, `confirm-complete`, `dispute`, `cancel`, customer review) must require `jobs.customer_id == current_user.id`.
- Provider job actions (`start`, `proofs`, provider review) must require `jobs.provider_id == providerProfileID(current_user.id)`.
- Provider `accept` should require a valid provider profile, a `POSTED` open-call job, no existing provider assignment, and should not allow accepting the provider's own customer-created job when that relationship exists.
- Admin routes should still be admin-only, not merely authenticated.

A common regression: `/jobs` hides foreign jobs, but direct `POST /jobs/{id}/confirm-complete` still mutates them. Always test direct-ID attacks.

## Frontend checklist

- Store bearer token in localStorage or the chosen app storage and attach `Authorization: Bearer <token>` from the API client.
- On 401, clear the token and return the user to login.
- Provide a clear login/register screen before private app flows.
- For demos, add explicit quick-login buttons with visible demo credentials rather than hidden hardcoded identities.
- Show the current user and role badges in the app shell.
- Adapt navigation by role so customer/provider/admin paths are not all visible to every user.
- Do not fetch admin dashboards or other privileged resources before confirming the current user has that role.

## Verification script pattern

Run both build checks and live HTTP checks through the deployed route when possible:

```bash
go test ./...
npm run build

# unauthenticated /me should fail
curl -s -o /tmp/noauth.json -w '%{http_code}' http://127.0.0.1/projects/<app>/api/v1/me

# invalid password should fail
curl -s -o /tmp/bad.json -w '%{http_code}' -X POST \
  http://127.0.0.1/projects/<app>/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.local","password":"wrong"}'

# valid login -> /me should pass
login=$(curl -fsS -X POST http://127.0.0.1/projects/<app>/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.local","password":"demo123"}')
token=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["token"])' <<<"$login")
curl -fsS http://127.0.0.1/projects/<app>/api/v1/me -H "Authorization: Bearer $token"

# direct-ID authorization attack should fail for an unrelated user
# create/register/login an unrelated customer, then attempt to mutate another customer's known job id.
```

## PRD/API contract update

When the requested work changes auth architecture, update the PRD/API contract artifact to document:

- New auth endpoints and which routes remain public.
- Session/token storage model.
- Role matrix and participant authorization rules.
- Demo credentials, if intentionally included for review.
- Acceptance checks for auth and authorization.
