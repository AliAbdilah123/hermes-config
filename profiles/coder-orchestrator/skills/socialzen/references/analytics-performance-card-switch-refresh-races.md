# Analytics performance, detail-card switching, and refresh races

Use this SocialZen-specific recipe when Analytics is slow, switching post-detail cards closes/crashes the view, or background refresh feels unstable.

## Investigate as three paths

1. **Overview load:** request count, payload size, SQL plan, server aggregation complexity, and render transforms.
2. **Detail selection:** determine whether the card uses overview data or a detail endpoint; test switching records with malformed dates, nullable metrics, missing media, and different targets.
3. **Refresh lifecycle:** enqueue, polling, terminal overview reload, visibility/focus resume, remount recovery, and concurrent filter changes.

Do not collapse all symptoms into one cause without evidence.

## Backend checks

- Inspect `apps/backend-go/analytics.go` for unbounded date-range results and full captions/media data.
- Run `EXPLAIN QUERY PLAN` on overview SQL. Correlated `post_media` subqueries behave like repeated database lookups; prefer one joined/CTE media selection only after confirming cost.
- Verify indexes support analytics filters/order, particularly `posts(user_id, ...)`, `post_targets(post_id,status,platform,account_id,published_at)`, and `post_media(post_id,position,id)`.
- Inspect ranking/comparison in `apps/backend-go/utils.go` for nested scans. Per-post scans of all other posts are O(n²); compute shared aggregates once where semantics permit.
- Benchmark seed data and a realistic generated dataset. Millisecond seed timings do not disprove scaling defects.
- Inspect worker cadence together with SQLite pool limits. A one-second idle refresh loop and multiple workers can contend with page traffic when the DB has one connection, even without `SQLITE_BUSY`.
- Keep polling responses compact until terminal state rather than repeatedly returning a large per-target results array.

## Frontend checks

- Count mount requests. In `AnalyticsPage.tsx`, a deep-link selection effect that changes `platform` retriggers the overview load and can request the full dataset twice.
- Sequence or abort overview requests. Filter loads and terminal refresh reloads can race; stale responses must not overwrite newer state.
- Keep detail selection independent from the global platform filter unless auto-filtering is explicit product behavior. Otherwise the selected post can disappear from the filtered response and look like a crash.
- Guard DTO dates and nullable metrics. Passing an empty backend date to `date-fns format(new Date(value))` throws `RangeError: Invalid time value`; use the shared safe formatter.
- Memoize repeated sorting/analysis across chart, insight, and table components.
- Audit duplicate video thumbnails with `preload="metadata"`; multiple surfaces can amplify media range requests.

## Refresh checks

- Prevent overlapping polls; pause while hidden and resume without duplicate loops.
- Deduplicate terminal handling so one job causes one background overview reload.
- Surface latest-job lookup failures after remount instead of swallowing them.
- Preserve current content during terminal reload.
- Treat restart recovery carefully: requeueing all `RUNNING` jobs may repeat provider calls unless they are idempotent.

## Minimum regression coverage

- Switch directly between cards with different/null/malformed fields.
- Deep-link selection does not cause an unintended duplicate load or disappearing modal.
- Out-of-order overview responses cannot replace newer filtered data.
- Refresh completion reloads once while keeping the page mounted.
- Remount resumes a nonterminal job and reports latest-job lookup failure.
- Hidden-tab and repeated-focus events do not create concurrent polling.
- A large synthetic dataset demonstrates acceptable query and aggregation growth.

## Reporting

Separate observed facts from scaling hypotheses. Include exact paths/lines, request counts, query plans or timings, payload sizes, focused test output, and uncovered cases. Label tiny local benchmarks as seed-only evidence, not production proof.