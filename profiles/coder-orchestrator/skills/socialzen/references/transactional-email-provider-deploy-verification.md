# Transactional email provider deploy verification

Use this when implementing or deploying the SocialZen auth-email provider phase from a PRD/plan.

## Durable details

- The Resend API key env var is `RESEND_KEY`; do not read or document `RESEND_API_KEY` for SocialZen.
- Expected env shape: `EMAIL_PROVIDER=resend`, `RESEND_KEY=...`, `EMAIL_FROM=...`, `APP_BASE_URL=...`, plus `AUTH_TOKEN_PEPPER` for token creation.
- The systemd unit currently reads `/home/ubuntu/socialzen/.env`, so deployment verification should check that file/service linkage before assuming `/opt/socialzen/.env` is authoritative.
- Forgot-password with an unknown email is the safest live smoke check because it exercises the endpoint response path without sending a real reset email.

## Compact verification recipe

```bash
cd /home/ubuntu/socialzen/apps/backend-go

go test . -run 'TestLoadConfigUsesRenamedResendKey|TestForgotPasswordIssuesHashedTokenWithoutLeakingUnknownUsers|TestResetPasswordConsumesTokenAndChangesPassword|TestVerifyEmailConsumesTokenAndResendRequiresSession'
go build -o /tmp/socialzen-api .

sudo install -m 755 /tmp/socialzen-api /opt/socialzen/socialzen-server
sudo systemctl restart socialzen.service
systemctl is-active socialzen.service
curl -sS -m 5 -w '\nHTTP %{http_code} total=%{time_total}s\n' http://127.0.0.1:8089/health

curl -sS -m 10 -w '\nHTTP %{http_code} total=%{time_total}s\n' \
  -H 'Content-Type: application/json' \
  -d '{"email":"missing-transactional-smoke@example.com"}' \
  http://127.0.0.1:8089/api/auth/forgot-password
```

Expected smoke response: `{"ok":true,"queued":true}` with HTTP 200.

## Pitfalls

- If `go test ./...` fails in unrelated legacy areas, do not treat it as an auth-email blocker; still report the unrelated failing packages/tests explicitly and keep the targeted auth-email tests green.
- Do not create a real signup/user just to test Resend delivery unless the user explicitly wants a live email send. Use unknown-email forgot-password for non-sending smoke.
