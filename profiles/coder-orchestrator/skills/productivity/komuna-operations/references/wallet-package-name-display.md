# Wallet package-name display fix

When wallet vouchers/pockets show only the product name (for example `Sunrise Vinyasa`) but a purchased package name should be visible (for example `Intro 5-Class`), check the **live Go API** first. The deployed Komuna service is `/home/ubuntu/projects/komuna/api/server` from the Go module in `/home/ubuntu/projects/komuna/api/v1`, even if TypeScript Cloudflare-worker sources also exist under `apps/api`.

## Durable pattern

1. Confirm the data exists in SQLite:
   - `vouchers.purchase_id` links to `purchases.id`.
   - `purchase_items.purchase_id` links the purchase to `purchase_packages.id`.
   - `package_entries` should be joined on both package and voucher product to avoid duplicate/wrong package metadata.
2. Patch the Go wallet handler (`api/v1/commerce_handlers.go`), not only `apps/api`, for the live site:
   - extend the wallet query with `purchase_items`, `package_entries`, and `purchase_packages`;
   - select `package_name`;
   - emit `package_name` and `display_name` on both wallet item and each voucher;
   - construct display names as `package · product`, but if the package already contains the product name, use the package name directly.
3. Keep frontend DTOs compatible by adding optional `package_name?: string | null` and `display_name?: string | null` to `VoucherDTO` and `WalletItemDTO`, then prefer `display_name` in wallet cards/tickets.
4. Add a Go regression test that seeds package + purchase + voucher rows and asserts `/api/v1/wallet` returns package/display metadata.
5. Verify with:
   - `go test .` in `api/v1`
   - `go build -o server .` in `api/v1`
   - relevant web tests/build if frontend changed.
6. Deploy live Go API by installing `api/v1/server` to `/home/ubuntu/projects/komuna/api/server` and restarting `komuna-api`; deploy web by copying `apps/web/dist/` to `/var/www/html/projects/komuna/`.

## Pitfalls

- Do not stop after changing `apps/api`: Cloudflare `wrangler deploy` may not be configured and is not the live path for this nginx/systemd deployment.
- If a user's vouchers are already `claimed`, the wallet's active voucher list may be empty even though the regression test is correct. Verify the API shape using seeded tests, not only the current user state.
- `vouchers` nullable columns scanned into Go strings should be selected with `COALESCE(...,'')` or scanned into nullable types; otherwise scan errors can silently leave later selected metadata empty if errors are ignored.
