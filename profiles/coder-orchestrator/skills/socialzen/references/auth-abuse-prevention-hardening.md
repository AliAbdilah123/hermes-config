# Auth abuse-prevention hardening

Use when implementing SocialZen auth hardening after core auth endpoints exist.

## Compact implementation pattern

- Add a small request guard early in `dispatch()` after `OPTIONS` handling and before route dispatch.
- Rate-limit sensitive auth endpoints by a stable key: normalized path + client IP + account/email where available. For Go `httptest`, strip the ephemeral port from `RemoteAddr` so tests do not bypass IP-based limits.
- For cookie-authenticated mutations, reject foreign `Origin` headers before reaching handlers. Allow missing `Origin` for curl/server-side clients and same-origin requests based on configured `FrontendBaseURL` or current request host.
- Session cookies should remain `HttpOnly`, `SameSite=Lax`, and set `Secure` when the request is HTTPS or forwarded as HTTPS (`X-Forwarded-Proto: https`).
- Add `auth_audit_logs` as a real SQLite table in BOTH migration paths: `db.go` test/back-compat migration and `internal/models/models.go` production `models.Migrate()`.
- Audit sensitive auth outcomes without raw passwords, raw tokens, or provider secrets. Good events: `signin_failed`, `signin_succeeded`, `signup_succeeded`, `google_signin_succeeded`, `csrf_rejected`, `rate_limited`.
- Add a server-side cleanup ticker in `main.go` for old used/revoked/expired `user_tokens`; keep cleanup idempotent and safe to run on startup.

## Targeted tests

Add tests that prove:

1. repeated bad login attempts return 429 after the limit;
2. cookie-authenticated POST with `Origin: https://evil.example` returns 403;
3. failed sign-in writes an `auth_audit_logs` row;
4. old used/revoked/expired token rows are deleted by cleanup;
5. HTTPS session cookie has `HttpOnly`, `Secure`, and `SameSite=Lax`.

## Verification recipe

```bash
cd /home/ubuntu/socialzen/apps/backend-go
gofmt -w auth_abuse.go auth_abuse_test.go auth.go google_auth.go routes.go main.go db.go internal/models/models.go
go test -run 'TestAuthRateLimit|TestCookieAuthenticated|TestAuthEvents|TestSessionCookie' .
go build -o /tmp/socialzen-api .
sudo install -m 755 /tmp/socialzen-api /opt/socialzen/socialzen-server
sudo systemctl restart socialzen.service
systemctl is-active socialzen.service
curl -sS -m 5 -w '\nHTTP %{http_code}\n' http://127.0.0.1:8089/health
sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT name FROM sqlite_master WHERE type='table' AND name='auth_audit_logs';"
for i in 1 2 3 4 5 6 7; do
  curl -sS -o /tmp/sz_auth_$i.json -w "$i %{http_code}\n" \
    -H 'Content-Type: application/json' \
    -H 'X-Forwarded-For: 203.0.113.77' \
    -d '{"email":"demo@brandorganizer.local","password":"wrongpassword"}' \
    http://127.0.0.1:8089/api/auth/sign-in/email
done
```

Expected smoke: health is 200, `auth_audit_logs` exists, and the 7th bad login returns 429.

## Pitfalls

- Do not only add the audit table to `db.go`; production startup calls `models.Migrate()`.
- Do not use raw `r.RemoteAddr` with its port for rate-limit keys; each test/request can get a new port.
- Do not parse or log request bodies in a generic guard just to extract email unless needed; if you do, restore the body for handlers.
- Full `go test ./...` may have unrelated historical failures in this repo; still run targeted tests and `go build`, and report unrelated full-suite failures honestly.
