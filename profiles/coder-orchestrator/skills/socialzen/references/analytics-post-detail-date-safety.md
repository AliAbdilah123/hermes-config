# Analytics post-detail date safety

Use when opening an Analytics post drill-down crashes React, especially after refresh/background-job changes or when provider data is sparse.

## Root-cause check

- Reproduce by rendering the real Analytics `PostDetailModal` with `publishedAt: ""` and an invalid non-date string.
- `date-fns/format(new Date(value), ...)` throws `RangeError: Invalid time value`; this is a render-time exception, so the whole route can appear to crash even though analytics fetching and refresh jobs succeeded.
- Trace the analytics SQL/DTO fallback: `COALESCE(..., '')` can legitimately produce an empty timestamp for incomplete historical/provider rows. A TypeScript `string` declaration does not prove the runtime value is a valid date.

## Smallest safe fix

- Parse once at the component boundary: `const publishedAt = new Date(post.publishedAt)`.
- Guard with `isValid(publishedAt)` before calling `format`.
- Render honest fallback copy such as `Posted date unavailable`; do not invent a timestamp and do not hide the entire post.
- Keep this independent from background refresh logic. A durable refresh queue prevents request-lifecycle freezes; it does not prevent malformed DTO values from crashing post-detail rendering.

## TDD and verification

1. Add a focused regression that renders the modal with an empty date and expects the fallback copy.
2. Run it first and confirm the pre-fix `RangeError`.
3. Apply only the guarded formatting change.
4. Run the focused modal test, Analytics refresh tests, typecheck, and production build.
5. Deploy the freshly built `dist/` before judging production. Old and new hashed Analytics chunks can coexist in the document root or local build output, so finding the guard in any `AnalyticsPage-*.js` is not proof that users load it. Fetch the cache-busted public `index.html`, read its current `index-*.js`, then read that index bundle's referenced `AnalyticsPage-*.js`; verify that exact public chunk is JavaScript and contains the guarded fallback marker.
6. Exercise both refresh/reload and post-detail opening. Build success, homepage HTTP 200, or a stale chunk containing the fix does not prove either runtime path.

## Test-selection pitfall

Vitest `-t` filters test names globally. Combining `-t 'one modal test'` with several files causes unrelated files to be reported as skipped; that is evidence for only the named test, not the whole listed set. Run the full focused Analytics file list separately when claiming the broader group passed.
