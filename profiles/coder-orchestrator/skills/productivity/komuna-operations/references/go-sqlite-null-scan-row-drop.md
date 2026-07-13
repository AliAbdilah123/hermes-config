# Go SQLite NULL scan row-drop pitfall

## Trigger

Use this when a Komuna list endpoint omits a known row even though direct SQLite queries show the row matches the filter, especially for session/product lists after activating a session.

## Pattern

In the Go+SQLite API, scanning nullable SQL columns directly into Go `string` variables fails when the value is `NULL`. Several handlers loop rows and do `if err := rows.Scan(...); err != nil { continue }`, which silently drops the row instead of surfacing the scan error.

Example shape:

```go
SELECT ..., p.slug, ...
...
var pslug string
if err := rows.Scan(..., &pslug, ...); err != nil {
    continue // hides NULL scan failure
}
```

If `p.slug` is NULL, the product/session can disappear from program-wide lists while still appearing on detail endpoints that use a different query/scanner.

## Investigation recipe

1. Verify the record in SQLite with the same joins and filters as the endpoint.
2. Compare detail endpoint vs aggregate/list endpoint responses.
3. Inspect the SELECT list for nullable columns scanned into primitive `string`, `int`, or `bool` variables.
4. Look for `rows.Scan` errors being ignored with `continue`.
5. Fix the boundary, not the data: either `COALESCE(nullable_col, '')` in SQL or scan into `sql.NullString` and map with `nilIfNullStr` / `nilIfEmpty`.
6. Replace silent `continue` with logging or an explicit error path when dropping the row would corrupt the list result.

## Minimal Komuna session-list fix shape

For program session lists that include product slugs, use:

```sql
COALESCE(p.slug,'')
```

instead of raw `p.slug` before scanning into a Go `string`.

## Verification

- Direct DB query shows the target row has `is_active=1`, product `status='active'`, and nullable field(s) such as `slug IS NULL`.
- Public/local list endpoint includes the row after fix.
- Product detail endpoint and program upcoming sessions endpoint agree for the activated product session.
