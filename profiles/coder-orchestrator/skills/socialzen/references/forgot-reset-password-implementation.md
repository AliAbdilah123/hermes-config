# Forgot/reset password implementation

When implementing SocialZen password recovery:

- Backend already has token foundation via `models.TokenService` and `user_tokens`; do not store raw reset tokens.
- `POST /api/auth/forgot-password` must stay enumeration-safe: return `200 { ok: true, queued: true }` for existing, unknown, and Google-only emails.
- Only issue password-reset tokens for users with a local password (`password_hash != ''`). Google-only users should not receive reset tokens until they add a SocialZen password through the intended settings/security flow.
- Reset links use `/auth/reset-password?token=<raw-token>` and the frontend route must call `POST /api/auth/reset-password` with `{ token, password }`.
- The reset endpoint consumes the token once, rejects reuse/expired tokens with `INVALID_OR_EXPIRED_TOKEN`, updates the password hash, and marks `email_verified=1`.

Minimal verification pattern:

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test . -run 'TestForgotPasswordIssuesHashedTokenWithoutLeakingUnknownUsers|TestResetPasswordConsumesTokenAndChangesPassword' -count=1

cd ../frontend
pnpm exec vitest run src/pages/ResetPassword.test.tsx
pnpm typecheck
pnpm build
```

Production smoke after deploy:

```bash
curl -sS -m 5 -X POST -H 'Content-Type: application/json' \
  -d '{"email":"missing-reset-smoke@example.com"}' \
  http://127.0.0.1:8089/api/auth/forgot-password
# Expected: {"ok":true,"queued":true}
```
