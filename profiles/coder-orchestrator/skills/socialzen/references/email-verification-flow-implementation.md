# Email verification flow implementation

Use this when implementing or debugging SocialZen email verification after the token/email foundation exists.

## Compact implementation shape

- Email/password signup must create `users.email_verified=0` and return `emailVerified:false`; do not leave the legacy default `true` behavior for password signup.
- Signup should create the session first, then queue `issueEmailVerification(...)` asynchronously so provider latency/failure does not block onboarding.
- Verification links should point at the frontend route (`/auth/verify-email?token=...`), whose page calls `POST /api/auth/verify-email`, then `authClient.refreshSession()` so UI state updates immediately.
- Keep Google sign-in verified when Google claims `email_verified=true`; this is separate from email/password verification.
- Gate restricted actions server-side, not just in the UI. Minimum durable gates:
  - post create/schedule/publish entrypoint: `internal/posts.Handler.CreatePost`
  - social account OAuth start: shared `oauthStartGeneric()` for Instagram/Facebook/Threads
- Return a specific `EMAIL_NOT_VERIFIED` error with clear copy so the frontend can show a resend/verify prompt.
- Resend verification stays session-gated and returns `{ok:true, alreadyVerified:true}` for verified users.

## Targeted checks

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test . -run 'TestEmailVerificationFlowGatesPublishing|TestResetPasswordConsumesTokenAndChangesPassword|TestVerifyEmailConsumesTokenAndResendRequiresSession|TestLoadConfigUsesRenamedResendKey|TestRequireAuthTokenPepper'
go test ./internal/models -run 'TestTokenService|TestNewTokenService|TestMigrateCreatesUserTokens'
go build -o /tmp/socialzen-api .

cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck
pnpm build
```

After deploy, verify the frontend route and JS asset content type:

```bash
curl -sI https://socialzen.ahsanworks.com/projects/socialzen/auth/verify-email?token=test | head -1
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<index-js>" | grep -i content-type
```
