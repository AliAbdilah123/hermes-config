# Local Go+SQLite email/password auth for migrated React/Vite apps

Use this reference when a migrated local-stack app previously had cloud auth (Neon/Better Auth, etc.) and needs first-party email/password auth without breaking public browsing or existing API client flows.

## Backend pattern

- Add auth tables alongside the local app DB initialization, not in a separate untracked store:
  - `auth_users(id, email unique, name, password_hash, created_at)`
  - `auth_sessions(token, user_id, expires_at, created_at)`
- Expose small JSON endpoints under the same API base path used by nginx/Vite:
  - `POST /auth/sign-up` validates email, enforces password length, hashes password, creates user, issues session.
  - `POST /auth/sign-in` verifies credentials and issues session.
  - `GET /auth/session` returns the current user for bearer/cookie session.
  - `POST /auth/sign-out` deletes the session and clears the cookie.
- Accept `Authorization: Bearer <token>` and an HttpOnly cookie so both API-client and browser-cookie paths work.
- Update the app's `currentUser(request)` equivalent to prefer a verified session user before falling back to the local dev/demo user.
- Do not print auth tokens in smoke-test commands or final summaries. If shell quoting would expose tokens in process args/logs, use a short Python/stdlib script that keeps the token in memory.

## Frontend pattern

- Keep the original cloud auth path available when its env var is configured, but make local mode a real auth client rather than a no-op fallback.
- Implement a tiny session store with `useSyncExternalStore` so existing `authClient.useSession()` consumers continue to react to sign-in/sign-out.
- Store the local bearer token in localStorage and return it from the existing `getJWTToken()` hook used by the API client.
- Replace “auth not configured” UI with email/password sign-in and sign-up forms in local mode.
- When adding new exports used by pages, update existing Vitest mocks for that module; otherwise tests can fail with “No <export> is defined on the mock.”

## Verification checklist

- Backend: `gofmt`, `go test ./...`, and `go build` from the local API directory.
- Frontend: production build and an auth-page targeted test if available.
- Smoke test the auth API locally and through the public nginx path:
  - sign-up returns 200 and a user email.
  - session lookup with bearer token returns 200 and same user email.
  - sign-in with correct password returns 200.
  - sign-in with wrong password returns 401.
- If deployed with systemd/nginx, rebuild the service artifact that the unit actually executes, restart service, verify `systemctl show ... -p EnvironmentFiles -p ActiveState -p SubState`, copy frontend dist to the actual public alias, and curl the public index/assets/API health.

## Pitfalls

- Do not leave the local auth fallback returning a permanent unauthenticated session once the user asks for email/password auth; it will make forms look present but never authenticate the app.
- Avoid relying only on full frontend test suites when they already have unrelated failures. Run a targeted auth test plus production build, and report unrelated suite failures separately.
- Browser navigation to subpath deployments can time out; curl the public index and JS bundle for auth strings/assets as a fallback, then use API smoke tests for functional proof.
