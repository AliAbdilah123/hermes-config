# Dashboard auth behavior

Newer Hermes releases require an explicit auth provider for non-loopback dashboard binds.

## Non-loopback bind gate

`0.0.0.0` / public binds fail unless configured:

- `dashboard.basic_auth.username` + `dashboard.basic_auth.password_hash` in `config.yaml`
- OAuth via `dashboard.oauth.client_id` / portal registration
- A `DashboardAuthProvider` plugin

There is **no unauthenticated public-bind option**. `--insecure` no longer bypasses this; the process exits with:

```
Refusing to bind dashboard to 0.0.0.0 — the auth gate engages on non-loopback binds, but no auth providers are registered.
```

If `Restart=always` is set, systemd will loop-restart forever with that message.

## Enable non-loopback access safely

1. Generate a password hash:
```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('your-password'))"
```

2. Set in `config.yaml`:
```yaml
dashboard:
  basic_auth:
    username: youruser
    password_hash: '<hash>'
    password: ''
    secret: ''
    session_ttl_seconds: 0
```

3. Restart the dashboard process; verify:
```bash
ss -tlnp | grep 9119
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119
```

## Why bare curl on `/api/*` returns 401

A plain `curl http://127.0.0.1:9119/api/version` does not carry the session token, so it gets `{"detail":"Unauthorized"}` unless basic auth headers or cookie session are used. This is correct behavior — it proves auth is active.

## Correct health check

Use the root path:
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119
```
