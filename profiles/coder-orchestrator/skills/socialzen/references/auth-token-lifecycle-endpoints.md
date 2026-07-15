# Auth token lifecycle endpoints

Use this when continuing SocialZen auth/security phases after the `user_tokens` foundation and email provider are present.

## Compact implementation pattern

- Keep `models.TokenService` as the single source for token lifecycle: `Create()` revokes older active tokens of the same user/type; `Consume()` checks type/hash/expiry/used/revoked and marks the row used in one transaction.
- Backend routes should expose the lifecycle directly:
  - `POST /api/auth/forgot-password` remains enumeration-safe and always returns `{ok:true, queued:true}` for existing and unknown emails.
  - `POST /api/auth/reset-password` consumes a `password_reset` token, requires a new password of at least 8 chars, updates `users.password_hash`, and rejects token reuse with `INVALID_OR_EXPIRED_TOKEN`.
  - `POST|GET /api/auth/verify-email` consumes an `email_verification` token and sets `users.email_verified=1`.
  - `POST /api/auth/resend-verification` requires an active session; if already verified, return `{ok:true, alreadyVerified:true}`, otherwise queue a fresh verification token/email.
- Reuse `queuePasswordReset()` / `issueEmailVerification()` helpers so token creation, URL generation, and email sending stay in one place.
- Do not log raw tokens or reset/verify URLs. Logging user IDs and provider errors is okay.
- Keep Resend config on `RESEND_KEY` only. Do not read or reference `RESEND_API_KEY`, even in regression tests.

## Tests / verification

Targeted tests should prove:

- forgot-password stores only a hashed token and does not reveal unknown users;
- reset-password consumes the token, changes the password, permits login with the new password, and rejects reuse;
- verify-email consumes the token and flips `email_verified`;
- resend-verification is session-gated;
- `RESEND_KEY` is the only Resend env key used.

Recommended backend check before deploy:

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test ./internal/models -run 'TestTokenService|TestNewTokenService|TestMigrateCreatesUserTokens'
go test . -run 'TestSignupStoresStrongPasswordHashAndLoginWorks|TestLegacyPasswordHashUpgradesAfterLogin|TestPasswordOnlyLoginRejectsGoogleOnlyUser|TestForgotPasswordIssuesHashedTokenWithoutLeakingUnknownUsers|TestResetPasswordConsumesTokenAndChangesPassword|TestVerifyEmailConsumesTokenAndResendRequiresSession|TestLoadConfigUsesRenamedResendKey|TestRequireAuthTokenPepper'
go build -o /tmp/socialzen-api .
```

Deploy backend only when frontend is unchanged, restart `socialzen.service`, verify `/health`, and smoke forgot-password with an unknown email to avoid sending a real reset link.