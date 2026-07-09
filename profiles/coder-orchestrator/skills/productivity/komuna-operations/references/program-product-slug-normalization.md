# Program/Product Slug Normalization

Use when the user asks to replace deprecated/random Komuna program or product slugs (for example `prog-yoga`) with name-based slugs.

## Safe workflow

1. Treat table IDs as internal stable primary keys. Do **not** rename `programs.id`, `products.id`, or dependent foreign keys.
2. Audit current production API and DB before mutating anything. The API may already return canonical `slug` values while the frontend still builds URLs from `id`.
3. Canonical rule: `slug = slugify(current name)` for both programs and products.
4. Preflight collisions before writes:
   - Program slugs should be globally unique.
   - Product slugs should be unique inside the same `program_id`.
5. Backup `sqlite.db`, `sqlite.db-wal`, and `sqlite.db-shm` before mutation.
6. If approved, update only `programs.slug` and `products.slug` in one transaction. Never delete/reseed production data for a slug-only fix.
7. Patch API create/update paths so future products persist `slugify(name)` and DTOs fallback to name-derived slugs if stored slug is blank.
8. Check frontend route builders separately: public links should prefer `program.slug ?? program.id` and `product.slug ?? product.id`; internal mutations may keep IDs.
9. Keep old ID routes resolving during transition. Add canonical redirects only after slug URLs are verified stable.

## Verification examples

```bash
curl -s https://komuna.ahsanworks.com/api/v1/programs/<program-slug> | jq '{id,name,slug}'
curl -s https://komuna.ahsanworks.com/api/v1/programs/<program-slug>/products | jq '.data[] | {id,name,slug}'
```

## Pitfall

Seeing an internal ID in the browser does not prove the production API slug is wrong. Verify API JSON first, then search the web app for URL construction that uses `.id` instead of `.slug`.
