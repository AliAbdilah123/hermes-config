# Auth Password Hardening Foundation

When executing SocialZen auth-security plans with a smallest-safe-diff constraint, implement the password foundation before larger verification/email UX work.

## Minimal durable shape

- Keep one canonical `users` row per person and `user_identities` for OAuth providers.
- Add `user_tokens` in **both** migration paths:
  - `apps/backend-go/db.go` test/legacy migration path.
  - `apps/backend-go/internal/models/models.go` production `models.Migrate()` path.
- Add targeted auth tests before deploying:
  - new signup stores a strong hash, not the legacy SHA-256 hash.
  - legacy SHA-256 password login still succeeds once and upgrades the stored hash.
  - Google-only users with empty `password_hash` get a clear `PASSWORD_NOT_SET` response on email/password login.

## Password helper pattern

Prefer a vetted dependency such as bcrypt/Argon2id if it is already present or dependency churn is acceptable. If the task is explicitly smallest-diff/no-new-dependency, stdlib PBKDF2-HMAC-SHA256 is an acceptable stepping stone:

- Store hashes as a versioned string such as `pbkdf2-sha256$<iterations>$<salt-b64url>$<hash-b64url>`.
- Keep legacy verification in a separate helper (`legacyPasswordHash`) so old demo/admin users continue to log in.
- On successful legacy login, immediately update `users.password_hash` to the new versioned format.
- Use constant-time compare for hash verification.

## Verification/deploy checklist

- Run targeted auth tests first, not only full suite, because this repo may have unrelated pre-existing failures.
- Run `go build -o /tmp/socialzen-api .` before deploy.
- Deploy backend binary, restart `socialzen.service`, and verify `/health`.
- Smoke login against localhost with a known demo account.
- Confirm the live DB has `user_tokens` after restart.
- Commit and push the backend changes after deployment.

## Pitfall

Full `go test ./...` can fail on unrelated OAuth/hashtag/Threads parity tests. Report those separately; do not let unrelated failures block a verified auth hot path when the targeted auth tests, build, migration, and smoke login pass.