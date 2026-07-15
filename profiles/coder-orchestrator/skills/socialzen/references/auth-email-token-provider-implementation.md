# Auth email token provider implementation

Use this when continuing SocialZen auth/security phases around verification, forgot/reset password, and transactional email.

## Implemented foundation shape

- Config uses `RESEND_KEY` for Resend. Do not read or reintroduce `RESEND_API_KEY`.
- `EMAIL_PROVIDER=resend` enables live Resend sending; empty/`test`/`none` is a no-send mode used by tests/dev.
- `EMAIL_FROM` and `APP_BASE_URL` are used for transactional templates and reset/verification URLs.
- `AUTH_TOKEN_PEPPER` remains required at backend startup; token creation uses `models.NewTokenService` and stores only HMAC token hashes in `user_tokens`.
- Signup creates the session first, then issues email verification asynchronously so an email-provider delay/failure cannot block account creation/login.
- Forgot-password returns the same generic `{ok:true, queued:true}` for existing and unknown emails; for existing users it issues a 30-minute `password_reset` token and sends the reset email.
- Provider errors are logged with user IDs only; never log raw tokens or reset/verify URLs.

## Verification pattern

Run targeted backend checks before deploy:

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test ./internal/models -run 'TestTokenService|TestNewTokenService|TestMigrateCreatesUserTokens'
go test . -run 'TestSignupStoresStrongPasswordHashAndLoginWorks|TestLegacyPasswordHashUpgradesAfterLogin|TestPasswordOnlyLoginRejectsGoogleOnlyUser|TestForgotPasswordIssuesHashedTokenWithoutLeakingUnknownUsers|TestLoadConfigUsesRenamedResendKey|TestRequireAuthTokenPepper'
go build -o /tmp/socialzen-api .
```

Deploy backend, restart `socialzen.service`, verify `/health`, and smoke forgot-password with an unknown email to avoid sending a real reset email during deployment verification.
