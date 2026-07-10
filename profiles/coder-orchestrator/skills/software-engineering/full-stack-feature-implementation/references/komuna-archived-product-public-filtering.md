# Komuna archived-product public filtering

Use when archived Komuna products still appear on public program/product/session views in the local Go + SQLite deployment.

## Durable lesson

The live Komuna deployment may be served by the local Go API binary at `/home/ubuntu/projects/komuna/api/server` (`komuna-api.service`), even though the repo still contains the older `apps/api` TypeScript/Cloudflare code. Before fixing public API behavior, verify the active service with:

```bash
systemctl show komuna-api.service -p ExecStart -p WorkingDirectory -p EnvironmentFiles --no-pager
```

Patch the Go source under `api/v1/` when that binary is active.

## Fix pattern

Archived products must be filtered at the API/query source, not only in React:

- Program detail product list: `productsForProgram` should include `WHERE program_id=? AND status='active'`.
- Product detail: `productByID` should include `WHERE id=? AND status='active'` so archived public product pages return not found.
- Product detail upcoming sessions: `sessionsForProduct` should join `products` and require `p.status='active'`.
- Program sessions page/API: both `programSessions` and `sessionList` should join/filter with `p.status='active'`.
- Product-specific sessions endpoint should also join `products` and require `p.status='active'`.

## Verification

Add/keep a Go test that archives a seeded product, inserts a session for it, then asserts:

- `GET /api/v1/programs/:program/products/:product` returns the existing not-found JSON behavior.
- `GET /api/v1/programs/:program` has no archived product ID in `products`.
- `GET /api/v1/programs/:program/sessions?page=1&limit=100` has no archived-product session.

Run:

```bash
cd /home/ubuntu/projects/komuna/api/v1
gofmt -w main_test.go queries.go program_handlers.go
go test ./...
go build -o server .
```

Deploy the Go binary carefully: if copying over `/home/ubuntu/projects/komuna/api/server` fails with `Text file busy`, stop the systemd service, copy, then start it again.

```bash
sudo systemctl stop komuna-api.service
cp /home/ubuntu/projects/komuna/api/v1/server /home/ubuntu/projects/komuna/api/server
sudo systemctl start komuna-api.service
systemctl is-active komuna-api.service
```

Smoke with `curl` and parse JSON (not broad string grep; program IDs can appear elsewhere): confirm `products[*].status` excludes `archived` and session payload does not include archived-product sessions.