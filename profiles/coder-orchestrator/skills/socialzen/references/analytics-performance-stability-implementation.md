# Analytics Performance and Detail Stability Implementation

Use after a read-only Analytics audit confirms slow overview loading, unstable post-detail switching, stale refresh responses, or SQLite contention.

## Minimal implementation sequence

1. **Write page-level regressions first**
   - Deep-linking with `postId`/`targetId` must open the detail without changing the global platform filter or issuing a second overview request.
   - Switching between posts must tolerate null/malformed `targets`, dates, and numeric metrics.
   - Resolve overview requests out of order and assert an older response cannot replace newer filter data.
   - Complete a refresh after changing filters and assert the background reload uses the latest filter values.

2. **Stabilize overview state**
   - Keep current request parameters in a ref when completion callbacks can outlive their render closure.
   - Increment a request-generation counter for every overview load; apply success, error, and loading state only when the generation is still current.
   - Do not couple detail selection to the page-wide platform filter. A detail deep link selects an already-loaded post; filtering the whole overview as a side effect amplifies requests and can remove the selected object.

3. **Harden the detail boundary**
   - Treat TypeScript DTO types as expectations, not runtime proof.
   - Validate finite numbers before `toLocaleString`, division, or `toFixed`.
   - Validate `targets` with `Array.isArray` and filter malformed elements before reading `platform`.
   - Use the shared safe-date formatter for missing or malformed provider timestamps.

4. **Remove repeated browser work**
   - Memoize ranking and insight computations by the posts-array identity.
   - A `WeakMap<PostAnalytics[], PostAnalytics[]>` is sufficient for a pure canonical top-post ranking shared by several components.
   - Use `preload="none"` for repeated video thumbnails in tables and insight cards; reserve metadata/content loading for the opened detail.

5. **Fix backend scaling at the source**
   - Replace per-post peer-average scans with one total/count pass, then subtract the current eligible post: `rate - (total-rate)/(count-1)`.
   - Select the first media row once and project both URL and media type from it; avoid two correlated subqueries for the same row.
   - Add only indexes proven by the query shape, typically `posts(user_id,id)`, `post_targets(post_id,status,account_id,platform,published_at)`, and `post_media(post_id,position,id)`.
   - Keep duplicate migration implementations aligned when SocialZen has both app-level and internal-model migrations.

6. **Reduce idle refresh contention without delaying new work**
   - Replace a one-second unconditional SQLite loop with a buffered wake channel plus a slower fallback timer.
   - Signal the worker immediately after a refresh job transaction commits.
   - Make signaling non-blocking so enqueue responses never wait for the worker.
   - Retain a fallback poll (for example five seconds) for restart/recovery and any missed wake.

## Verification boundaries

- Run focused Analytics frontend tests, typecheck, and production build.
- Run focused Go Analytics tests independently from the full suite; report unrelated pre-existing failures separately.
- Before commit, stage only intended source/tests and explicitly exclude the modified runtime SQLite database and unrelated review artifacts.
- After deployment, verify: service active, local/public health 200, public HTML references the new asset, and the served Analytics chunk contains stable implementation markers. HTTP 200 alone is not deployment proof.
- Authenticated browser exercise remains the strongest end-to-end check; when unavailable, say so and rely only on the exact page-level regressions and served-asset evidence actually obtained.

## Pitfalls

- Do not claim cancellation if the implementation only ignores stale responses; call it request sequencing.
- Do not add pagination unless product behavior permits it; first remove quadratic work and repeated lookups while preserving the API contract.
- Do not commit generated `dist/` unless the repository tracks it.
- A successful push does not deploy SocialZen: build the Go binary, install it at the systemd `ExecStart` path, publish the frontend `dist/` to the nginx document root, restart, and verify both origin and public routes.
