# SocialZen Google Sign-In via GIS ID Tokens

Use when implementing or debugging SocialZen app-login with Google. This is distinct from Meta/Instagram/Facebook account-connect OAuth used after login.

## Architecture

- Frontend uses Google Identity Services (GIS) popup/prompt to obtain a Google ID token credential.
- Frontend posts `{ "credential": "<jwt>" }` to `POST /api/auth/sign-in/google`.
- Backend verifies the ID token server-side using Google JWKS and the configured Google client ID.
- After verification, SocialZen still issues its normal DB-backed `brand_session` cookie. Do not add a second browser auth system or store Google tokens for app-login.

## Durable implementation shape

Backend:
- `appConfig` should include public Google client ID config (`GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_CLIENT_ID`) and optional `GOOGLE_JWKS_URL` for tests.
- Expose non-secret Google client ID in `/api/config/status` so the frontend can initialize GIS without baking a stale value into the bundle.
- Add `POST /api/auth/sign-in/google` in `routes.go`.
- Add a `user_identities` table with `(provider, provider_subject)` unique and `(user_id, provider)` unique.
- Verify token checks: RS256 signature from JWKS, `aud == GoogleClientID`, Google issuer, `exp`, non-empty `sub`, and verified email.
- Link existing users by verified email only; otherwise create a new Google-only user.
- Google-only users should have empty password hash (or nullable hash after a future rebuild). Email/password sign-in must reject empty password hashes.
- Keep both migration paths in sync: `db.go` test migration and `internal/models/models.go` production migration.

Frontend:
- Add `authClient.signIn.google({ credential })`.
- Load `https://accounts.google.com/gsi/client` lazily from a small helper; avoid shipping a new dependency.
- Resolve client ID from `VITE_GOOGLE_CLIENT_ID` if present, otherwise `/api/config/status`.
- After successful Google sign-in, call `authClient.refreshSession()` before routing to avoid stale module-level session cache.
- Preserve existing `plan` and `from` redirect behavior.
- Remove/relabel Instagram from app-login screens; SocialZen Instagram OAuth is a protected publishing-account connect flow, not app auth.

## Verification

- Targeted backend tests for: new Google user creates `user_identities` + session, verified email links to existing user, unverified email returns 403.
- `go build -o /tmp/socialzen-api .`
- `pnpm typecheck && pnpm build`
- Deploy backend/frontend, then verify:
  - `systemctl is-active socialzen.service` is active.
  - `/api/config/status` returns `google.configured: true` and the public client ID only.
  - Invalid credential returns controlled `401 GOOGLE_TOKEN_INVALID` JSON.
  - Public JS asset content type is `application/javascript` and deployed lazy chunk contains the Google sign-in copy/marker.

## Pitfalls

- Do not use the Google OAuth redirect URI intended for authorization-code flows as the core GIS path. For GIS popup/callback, Authorized JavaScript Origin is the key Google Console setting.
- Do not store Google access/refresh tokens for app-login unless the product later needs Google API access.
- Do not rely on source/env inspection alone; verify the deployed `/api/config/status` and public bundle after deploy.
- Full repo tests may contain unrelated legacy failures; run targeted Google auth tests plus build/typecheck and report unrelated full-suite failures honestly.