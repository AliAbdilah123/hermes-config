# Live Go API session visibility pitfall

## When to use

Use this when debugging Komuna public Program Detail, Product Detail hero sessions, or All Upcoming Sessions visibility.

## Lesson

Komuna currently has both a newer `apps/api` Cloudflare Worker code path and the live local Go API path under `api/v1`. The public site uses `window.__API_BASE__ = "/api/v1"`, served by `komuna-api.service` from `/home/ubuntu/projects/komuna/api/server`.

If a public session-card bug is still visible after changing `apps/api`, verify the live `/api/v1` Go handler before claiming the fix is deployed.

## Session-card visibility source

Program Detail, Product Detail hero sessions, and All Sessions/Upcoming Sessions all use the program session-card endpoint shape:

```text
GET /api/v1/programs/:programId/sessions?status=upcoming&productId=:productId&page=1&limit=N
```

The live Go handler is `api/v1/program_handlers.go` → `programSessions()`.

For public listings, inactive sessions must be excluded at SQL level:

```sql
... WHERE p.program_id=? AND p.status='active' AND s.is_active=1
```

Otherwise template-created future sessions with `status='scheduled'` and `is_active=0` compute to `upcoming` and leak onto public cards.

## Verification pattern

After rebuilding/restarting the Go API, verify the public endpoint directly, not just the UI:

```bash
cd /home/ubuntu/projects/komuna/api/v1
go test ./...
go build -o ../server .
sudo systemctl restart komuna-api.service
systemctl is-active komuna-api.service
curl -sS 'https://komuna.ahsanworks.com/api/v1/programs/prog-yoga/sessions?status=upcoming&productId=prod-yoga-sv&page=1&limit=10'
```

Expected for inactive-only future sessions: `items: []`, `total: 0`.

## Pitfall

Do not assume the TypeScript Worker path is live just because it has matching domain logic. Check the frontend `window.__API_BASE__` or the public API response shape first. The Go API response includes fields such as `productSlug`, `managerImageUrl`, and `limit:100` in this endpoint.
