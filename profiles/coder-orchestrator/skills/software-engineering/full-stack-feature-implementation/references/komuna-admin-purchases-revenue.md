# Komuna admin purchases tab + live revenue totals

Use when adding/supporting Komuna admin purchase-history views or fixing dashboard revenue in the local Go + SQLite + Vite deployment.

## Durable lessons

- The active Komuna deployment may be the local Go API at `/home/ubuntu/projects/komuna/api/server`, not the old TypeScript API under `apps/api`. Trace `systemctl cat komuna-api.service` and active listen port before editing backend code.
- Existing frontend API support for program purchases can be reused: `apiClient.listProgramPurchases(programId)` calls `/programs/:id/purchases`. Prefer enriching that endpoint over adding a duplicate admin-only endpoint.
- The Management revenue card must come from real paid purchases, not fixture constants. Query through `purchases -> program_members` scoped by `pm.program_id`, filter `pu.status='paid'`, and month-bound by `pu.created_at >= start_of_month`.
- The Purchases tab belongs between Packages and Vouchers because purchases are the bridge between package sale and voucher issuance.
- A useful admin purchases payload includes `member_email`, `member_name`, package `items`, voucher list/statuses, invoice/payment metadata, total amount, status, and `created_at`, sorted newest-first.
- Share frontend currency/summary helpers between Management and Purchases so the two revenue cards display the same way.

## Verification recipe

1. Add/adjust a Go test that seeds two paid purchases for one program member and asserts:
   - `/api/v1/programs/<program>/admin/dashboard` returns the summed `revenue_this_month`.
   - `/api/v1/programs/<program>/purchases` returns both rows with member email.
2. Run from `api/v1`: `go test ./...`.
3. Run frontend production build from `apps/web`: `npm run build`.
4. Deploy:
   - `go build -o /home/ubuntu/projects/komuna/api/server .` from `api/v1`.
   - `sudo systemctl restart komuna-api.service`.
   - `rsync -a --delete apps/web/dist/ /var/www/html/projects/komuna/`.
5. Smoke with an existing session token without printing it: use a small Python script to read the token from SQLite, call localhost API, and print only program name, revenue, and purchase row summaries.

## Pitfalls

- Do not create live payment-provider transactions to verify this; seeded tests and local API reads are enough.
- Avoid dumping auth tokens or `.env` contents in terminal output. Print token length at most, preferably nothing.
- If full frontend Vitest is noisy with unrelated existing failures, still run the app production build and targeted/new tests; report the unrelated suite state separately.