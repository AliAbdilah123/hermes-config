# Program/Product/Package Seed Quality Audit

Use this reference when a user reports mismatched program/product URLs, missing packages, missing product/package images, free packages, or currency display bugs in Komuna.

## Read-only investigation checklist

Before planning or fixing, inspect the **active live SQLite DB** and current frontend/API code. Do not infer from seed files alone.

### DB checks

```sql
-- Program slugs should be human-readable, not blank/ID-only.
SELECT id, name, slug FROM programs ORDER BY name;

-- Products historically may lack a slug column. Check schema first.
PRAGMA table_info(products);
SELECT id, program_id, name, image_url FROM products ORDER BY program_id, name;

-- Packages may be absent for most programs; check coverage and free packages.
SELECT p.id, p.name, COUNT(pp.id) AS package_count
FROM programs p
LEFT JOIN purchase_packages pp ON pp.program_id = p.id
GROUP BY p.id
HAVING package_count = 0;

SELECT id, program_id, name, price
FROM purchase_packages
WHERE CAST(price AS REAL) <= 0 OR price IS NULL OR TRIM(price) = '';

-- Package images may require a schema addition.
PRAGMA table_info(purchase_packages);
```

### Typical durable root causes

- `programs.slug` can be blank for all seeded programs, so detail URLs fall back to internal IDs such as `prog-sydney`.
- `products` may not have a `slug` column at all; product detail routes then expose IDs such as `prod-yoga-sv` even when the display name is `Sunrise Vinyasa`.
- `products.image_url` can be empty for all products.
- `purchase_packages` may have no `image_url` column, so package showcase images require schema + DTO support.
- Package seeding may be incomplete: a small number of programs have packages while many programs, including the reported one, have none.
- Free package check should be explicit (`price <= 0`) even if the current DB has none; reseeding can reintroduce free rows.

## Fix pattern after approval

1. Back up `sqlite.db`; never delete it for reseeding.
2. Add missing schema fields idempotently (`products.slug`, `purchase_packages.image_url`) through the Go schema/migration path.
3. Backfill `programs.slug` and `products.slug` from names with a deterministic slugify function. Route resolution must remain additive: ID links and slug links both work.
4. Backfill non-empty `products.image_url` and package `image_url` values.
5. Ensure every program has at least one **paid** active package with valid `package_entries`.
6. Return new fields from Go DTOs and add frontend TS fields (`product.slug`, `package.imageUrl`).
7. Verify with SQL counts plus public API/UI smoke checks.

## Frontend audit points

- Product detail can have two upcoming-session sections: current working hero-side section plus an older lower `SessionsSection`. Remove only the old lower section; keep packages/store.
- Session instance cards should separate click targets: primary click goes to the filtered sessions page, and a small `See product details` link below datetime goes to product detail.
- Replace local hardcoded USD formatting on dashboards/purchases with the shared `formatPriceLabel` currency helper.
- For money overflow, prefer a tiny shared CSS/class fix: `font-size: clamp(...)`, `overflow-wrap:anywhere`, `font-variant-numeric: tabular-nums`.
- Verify `apps/web/.env` has `VITE_USD_TO_IDR_RATE`; Vite will not read a root `.env` value without the `VITE_` prefix in the web app build root.
