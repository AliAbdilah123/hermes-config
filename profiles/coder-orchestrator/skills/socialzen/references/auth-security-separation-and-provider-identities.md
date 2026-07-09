# Auth security separation and provider identities

Use when planning or implementing SocialZen app-login changes involving email/password, Google Sign-In, future OAuth providers, or password management.

## Current architecture fit

- Keep `users` as the canonical SocialZen account/person table.
- Use `user_identities` as the provider identity table instead of adding provider-specific columns to `users`.
- `user_identities` already exists in both migration paths:
  - `apps/backend-go/db.go`
  - `apps/backend-go/internal/models/models.go`
- Existing Google Sign-In flow already verifies GIS ID tokens on the backend and links through `user_identities`.

## Recommended identity model

```sql
users(id, name, email unique, password_hash, avatar_url, timezone, email_verified, created_at)
user_identities(id, user_id, provider, provider_subject, email, email_verified,
                name, avatar_url, raw_profile_json, created_at, updated_at, last_login_at,
                UNIQUE(provider, provider_subject), UNIQUE(user_id, provider))
```

Why this beats provider columns on `users`:

- Future providers (`google`, `github`, `microsoft`, `apple`) add rows, not schema columns.
- `provider_subject` stores the stable provider ID (Google `sub`, GitHub numeric ID, etc.).
- Email/password and OAuth methods can coexist on the same `users.id`.
- Provider email changes do not create duplicate users because lookup starts from `(provider, provider_subject)`.

## Required auth behavior

### Email/password signup

- Only `/api/auth/sign-up/email` creates email/password accounts.
- Normalize email with `strings.ToLower(strings.TrimSpace(email))`.
- Existing email returns `409 USER_ALREADY_EXISTS`.
- Store password with bcrypt or Argon2id, not SHA-256.

### Email/password login

- `/api/auth/sign-in/email` must never create accounts.
- Unknown email returns `401 INVALID_EMAIL_OR_PASSWORD`.
- Google-only users with empty `password_hash` return a specific `PASSWORD_NOT_SET` style error and user-facing copy directing them to Settings → Security → Add Password.
- Existing SHA-256 hashes should be verified once and transparently upgraded to bcrypt after successful login to avoid forcing resets.

### Google Sign-In

Lookup/link order:

1. Find `user_identities(provider='google', provider_subject=<google sub>)`; login that user.
2. If no identity, link to an existing `users.email` only when Google email is verified.
3. If no matching user, create a Google-only user with no password hash and insert the identity.
4. If `sub` belongs to one user but verified email implies another, reject with an account-link conflict instead of creating/merging silently.

Always use Google `sub` as the provider identifier. Email is only a verified linking hint.

### Add/Change Password UX

Add Settings → Security:

- Email/password users see **Change Password** with current password, new password, confirm new password.
- Google-only users see **Add Password** with new password and confirm new password; active session is the minimum V1 verification, email-code re-verification can be a policy choice.
- The feature changes only the SocialZen account password, never the user’s Google account password.
- Keep the current session active by default. “Log out other sessions” can be V2 unless explicitly requested.

## Implementation checklist

- Update password hashing helpers in `apps/backend-go/utils.go`.
- Update `apps/backend-go/auth.go` signup/login/password endpoints.
- Harden `apps/backend-go/google_auth.go` conflict handling.
- Add frontend API methods in `apps/frontend/src/lib/auth.ts` or a small `security.ts` if needed.
- Add Security tab in `apps/frontend/src/pages/settings/SettingsPage.tsx`, between Profile and Connected Accounts.
- Add auth rate limiting to sign-in, sign-up, Google sign-in, and password endpoints.
- Ensure cookies remain `HttpOnly`, `SameSite=Lax`, and set `Secure=true` for HTTPS deployments.
- If schema changes are required, update BOTH migration paths (`db.go` and `internal/models/models.go`). Avoid schema churn if empty password hash already models Google-only accounts.

## Verification checklist

- Unknown email login returns 401 and does not create a `users` row.
- Email signup stores a bcrypt/Argon2id hash.
- Existing legacy SHA-256 user can login and hash upgrades.
- Email/password user later signing in with Google same verified email links one `user_identities` row to the same user.
- Google-only user cannot password-login until Add Password.
- After Add Password, the same user can authenticate by Google or email/password.
- Provider conflict cases are rejected, not silently merged.
- Auth rate limit returns 429 after repeated failures.
