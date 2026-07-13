# Auth Token Foundation

Use this when adding password-reset, email-verification, magic-link, or invite token support.

## Durable implementation shape

- `AUTH_TOKEN_PEPPER` is a required environment variable for token HMAC hashing. Do not hardcode it and do not silently fall back to a dev value.
- Startup should fail clearly if `AUTH_TOKEN_PEPPER` is missing, before serving traffic.
- Store only `HMAC-SHA256(rawToken, AUTH_TOKEN_PEPPER)` in `user_tokens`; return/send the raw token only once.
- `user_tokens` should be created in both migration paths:
  - `apps/backend-go/internal/models/models.go` (`models.Migrate`, production startup)
  - `apps/backend-go/db.go` (`app.migrate`, tests/legacy path)
- Prefer a single typed table for short-lived auth actions:
  - `type`: `email_verification`, `password_reset`, `magic_link`
  - `token_hash`, `expires_at`, `used_at`, `revoked_at`
  - request metadata such as email/IP/user-agent when useful
- Indexes to keep:
  - unique `(type, token_hash)` lookup
  - `(user_id, type, used_at, revoked_at, expires_at)` for active-token cleanup
  - `expires_at` for cleanup jobs

## TokenService behavior

- Create: validate user/type/TTL, generate 32 random bytes as base64url, revoke existing active tokens for the same user+type, insert hashed token.
- Consume: lookup by type+hash where `used_at IS NULL`, `revoked_at IS NULL`, and `expires_at > now`; set `used_at` in the same transaction.
- Reject wrong type, expired, used, revoked, and blank tokens with one safe invalid-token error.

## Tests

Add targeted tests for:

- missing pepper returns a clear `AUTH_TOKEN_PEPPER` error
- migration creates `user_tokens` and expected indexes
- raw token is never stored
- token can be consumed exactly once
- creating a replacement token revokes the previous active token of the same user/type
- expired and wrong-type tokens are rejected

Run targeted tests plus `go build` before deploy. Full `go test ./...` may have unrelated legacy failures; report them separately instead of blocking a verified token foundation.