# Product slug creation/backfill and hidden session rows

Use when a Komuna product exists but routes/session lists behave inconsistently, especially newly created products whose detail page works but program-wide upcoming sessions omit their activated sessions.

## Root cause pattern

The live Go+SQLite API can fail silently when a SELECT scans nullable slug columns into Go `string` variables. In `programSessions`, a `NULL` `products.slug` caused `rows.Scan(...)` to fail; the loop swallowed the scan error with `continue`, so the session disappeared from the program-wide upcoming sessions endpoint while product detail still showed it.

## Diagnosis

1. Confirm the product/session exist in SQLite:
   - `products.id`, `products.name`, `products.slug`, `products.status`
   - `sessions.product_id`, `sessions.status='scheduled'`, `sessions.is_active=1`, future `start_time`
2. Compare endpoints:
   - product detail: `/api/v1/programs/:program/products/:product`
   - program sessions: `/api/v1/programs/:program/sessions?status=upcoming&page=1&limit=100`
3. If product detail includes the session but program-wide sessions do not, inspect query scans for nullable fields (`p.slug`, image, manager columns) scanned into plain strings.
4. Count missing product slugs:
   - `SELECT id,name FROM products WHERE slug IS NULL OR slug='';`

## Fix pattern

- Product creation must insert `slug = slugify(name)`.
- Startup/open migration should backfill existing rows:
  - `UPDATE products SET slug=slugify(name) WHERE slug IS NULL OR slug=''` implemented in Go by selecting rows and applying the existing `slugify` helper.
- Program sessions query should use `COALESCE(p.slug,'')` so legacy/null data cannot hide rows.
- Prefer also surfacing scan errors during future debugging; silent `continue` makes data bugs look like filtering bugs.

## Verification

- Regression test: create a product through the API and assert response `slug` equals slugified name.
- Run Go tests from `api/v1`: `go test .`
- Verify DB: `SELECT COUNT(*) FROM products WHERE slug IS NULL OR slug='';` returns `0`.
- Verify public API with a browser-like user agent if Cloudflare blocks default clients:
  - `/api/v1/programs/:program/sessions?status=upcoming&page=1&limit=100`
  - Confirm affected session appears and `productSlug` is populated.
