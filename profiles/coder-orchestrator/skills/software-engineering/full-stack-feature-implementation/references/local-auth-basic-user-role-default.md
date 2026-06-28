# Local auth basic-user role default

Use this reference when adding or fixing first-party email/password auth in a migrated local Go/SQLite app that still has a demo/dev workspace fallback.

## Durable lesson

Do not let the unauthenticated/demo workspace fallback bleed into real authenticated users. A signed-up user with no explicit program membership should remain a basic user with no program-scoped role.

Expected workspace response for a brand-new signed-up user:

```json
{
  "isSuperAdmin": false,
  "programs": []
}
```

They should not automatically receive any of:

- platform/super-admin status
- program `admin`
- program `manager`
- program `member`

## Implementation pattern

In the workspace/current-user endpoint, distinguish three cases explicitly:

1. Authenticated session/cookie/bearer token user — return only real memberships/roles found in persisted state.
2. Explicit development override header (for example `X-Komuna-User`) — treat as explicit caller identity, not as implicit super-admin unless the app intentionally defines that behavior.
3. No authenticated user and no explicit override — only here may an old demo/admin fallback synthesize access for a public demo environment.

Example guard shape:

```go
uid, email, name := a.currentUser(r)
_, authenticated := a.userFromRequest(r)
explicitDevUser := r.Header.Get("X-Komuna-User") != ""
useDemoAdminWorkspace := !authenticated && !explicitDevUser

// Build progs from persisted program members first.
// Only synthesize demo admin roles when len(progs)==0 && useDemoAdminWorkspace.
// Return isSuperAdmin: useDemoAdminWorkspace.
```

## Regression test recipe

Write a backend test that:

1. Creates a temp SQLite DB via env override.
2. Calls `POST /api/v1/auth/sign-up` with a unique email/password.
3. Uses the returned token/cookie to call `GET /api/v1/me/workspace`.
4. Asserts:
   - HTTP 200
   - `isSuperAdmin == false`
   - `len(programs) == 0`
   - no role objects include `admin`, `manager`, or `member`

Watch this test fail before the fix; the failure commonly shows `isSuperAdmin: true` or synthesized program roles.

## Public verification

After deploying the rebuilt API, do a non-secret public smoke test against the live API path:

1. Sign up a throwaway unique email.
2. Call workspace with the returned bearer token.
3. Print only safe summary fields, for example `{isSuperAdmin, programCount}`.
4. Fail the smoke test if `isSuperAdmin` is true or `programCount > 0`.

Do not print passwords, session cookies, full env files, or secret-bearing config.
