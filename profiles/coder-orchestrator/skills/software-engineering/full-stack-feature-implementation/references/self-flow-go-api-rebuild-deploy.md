# Self-Flow Go API Rebuild & Deploy

## Binary path trap

The systemd service runs `packages/api/v1/server` (from `ExecStart=/home/ubuntu/projects/self-flow/packages/api/v1/server`), but the natural `go build -o ../server .` puts the binary at `packages/api/server` (parent dir). The service **will not pick up changes** from `packages/api/server`.

Correct rebuild:
```bash
cd /home/ubuntu/projects/self-flow/packages/api/v1
CGO_ENABLED=1 go build -o server .
sudo systemctl restart self-flow-api
```

## Go build cache

After editing source, `go build` may serve a cached stale binary. If the running binary doesn't reflect your source change:
```bash
cd /home/ubuntu/projects/self-flow/packages/api/v1
go clean -cache
CGO_ENABLED=1 go build -o server .
sudo systemctl restart self-flow-api
```

Verify with `strings server | grep "unique_literal_from_your_change"` or test the endpoint.

## Response wrapping convention

All Go API endpoints wrap responses in `{"data": ...}`:
```go
jsonOK(w, Item{"data": ...})
```

If an endpoint returns unwrapped (e.g. `Item{"dataPoints": pts}`), the frontend's `fetchAPI<T>` generic expects the `data` key, so `response.data` will be `undefined` and the UI will show empty/fallback state. This is the #1 cause of "data exists in DB but UI shows nothing."

## Service info

- Service: `self-flow-api`
- Port: `:8096` (localhost only)
- DB: `/home/ubuntu/projects/self-flow/sqlite.db`
- Binary: `/home/ubuntu/projects/self-flow/packages/api/v1/server`
- Frontend: nginx serves `/var/www/html/projects/self-flow` at `selfflow.ahsanworks.com`
- API proxy: nginx proxies `/api/` → `http://127.0.0.1:8096/api/`

## Testing focus graph

```bash
# Get a token
TOKEN=$(curl -s http://localhost:8096/api/auth/signin \
  -H 'Content-Type: application/json' \
  -d '{"email":"test-focus@example.com","password":"test123"}' | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")

# Test graph endpoint
curl -s "http://localhost:8096/api/focus/graph?startDate=2026-06-02&endDate=2026-07-02" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Verify response has 'data' key (not bare dataPoints)
```
