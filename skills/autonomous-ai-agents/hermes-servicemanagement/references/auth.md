# Dashboard auth behavior

The Hermes dashboard uses an ephemeral session token rather than long-lived API keys for frontend auth.

## How it works

1. On startup, `web_server.py` generates an ephemeral `_SESSION_TOKEN` (`secrets.token_urlsafe(32)`)
2. When the SPA requests `/`, the server injects this token into `index.html` as `window.__HERMES_SESSION_TOKEN__="..."`
3. Frontend JS reads the token from `window` and sends it on `/api/*` calls
4. If auth is gated (`auth_required=True`), the SPA reads identity from `/api/auth/me` over cookie auth instead; the legacy token path is not used

## Why bare curl on `/api/*` returns 401

A plain `curl http://127.0.0.1:9119/api/version` does not carry the session token, so it gets `{"detail":"Unauthorized"}`. This is correct behavior — it proves token auth is active.

## Correct health check

Use the root path:
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119
# Expect 200, and HTML contains window.__HERMES_SESSION_TOKEN__
```

Or pass the token explicitly:
```bash
TOKEN=$(curl -s http://127.0.0.1:9119/ | sed -n 's/.*window.__HERMES_SESSION_TOKEN__="\([...1/p')
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:9119/api/version
```

## Legacy/code references

- Token injection: `web_server.py` around line 17302
- Verification: `_verify_session_token()` around line 356
- WS auth: `/api/ws` legacy `?token=` path around line 15974
