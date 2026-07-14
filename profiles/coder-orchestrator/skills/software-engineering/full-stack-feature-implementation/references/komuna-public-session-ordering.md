# Komuna public session ordering and product scoping

Use when fixing public Komuna upcoming-session lists on program detail, product detail, or sessions pages in the local Go + SQLite API.

## What to centralize

Session ordering should live in the Go API, not per-page frontend sorting:

- `sessionsForProduct(productID)` for product detail `upcoming_sessions`
- `sessionList(programID)` for program/member summary lists
- `programSessions(programID)` for the card/list endpoint used by sessions pages and product-detail hero previews

Sort order:

1. `s.start_time ASC`
2. `s.end_time ASC`
3. alphabetical fallback: `LOWER(COALESCE(NULLIF(s.title,''), p.name)) ASC`

A tiny helper like `sessionSortSQL()` keeps the order consistent across query paths.

## Important pitfall: product detail hero uses `programSessions`

The product detail frontend may already send:

```ts
apiClient.getProgramSessions(programId, {
  status: 'upcoming',
  productId: product.id,
  page: 1,
  limit: 3,
})
```

If `programSessions` ignores `?productId=...`, the hero/right-column "Upcoming sessions" preview leaks all active program sessions even though the product-detail endpoint's `upcoming_sessions` is correctly product-scoped.

Fix pattern in `programSessions`:

1. Read `productFilter := r.URL.Query().Get("productId")`.
2. If present, resolve ID/slug with `a.resolveProductID(programID, productFilter)`.
3. Add `AND (?='' OR s.product_id=?)` to the SQL WHERE clause.
4. Pass `productID, productID` as query args.
5. Keep status filtering in-memory if it already relies on computed `cardStatus`.

## Regression test shape

Extend the session-order test to insert:

- multiple sessions for target product with out-of-order start times
- two sessions with the same start/end window and titles that prove alphabetical tie-break
- an earlier session for a different product

Assertions:

- product detail `upcoming_sessions` returns only the target product in sorted order
- `/programs/:id/sessions?productId=<target>&page=1&limit=...` returns only the target product in the same sorted order

This catches both the original ordering bug and the follow-up product-scope leak.
