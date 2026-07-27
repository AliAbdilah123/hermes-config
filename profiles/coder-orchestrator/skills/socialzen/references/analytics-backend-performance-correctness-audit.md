# Analytics backend performance and correctness audit

Use this checklist when analytics overview, post drill-down, or refresh feels slow, hangs, crashes, or returns contradictory metrics.

## Trace the complete request path

1. Map backend routes to overview, refresh enqueue, latest-job, and job-detail handlers.
2. Trace the frontend overview fetch, refresh polling, post selection, and modal/detail rendering.
3. Verify whether “detail” is a real endpoint. In SocialZen, the analytics post modal may render the post object already included in the overview payload; card-switch latency or crashes can therefore be frontend/data-contract problems rather than detail-handler latency.
4. Check recent commits and focused tests before attributing behavior to current code; analytics stability fixes can materially change the diagnosis.

## SQL and scaling checks

- Record table sizes and run `EXPLAIN QUERY PLAN` on the exact overview query.
- Look for missing composite indexes on the actual filter/join/order columns, especially:
  - `posts(user_id, ...)`
  - `post_targets(post_id, status, platform, account_id, published_at)`
  - `post_media(post_id, position, id)`
- Treat correlated media/account subqueries as database-level repeated lookups even when there is no Go loop issuing one query per row.
- Check for unbounded overview responses: returning every matching post, full captions, all targets, and media fields makes SQL, JSON encoding, network payload, and browser work grow with account history.
- Inspect in-memory post ranking and comparisons as well as SQL. A loop that computes each post against every other post is O(n²) and can dominate after the query returns.

## SQLite locks and refresh concurrency

- Inspect `SetMaxOpenConns`, WAL, and busy timeout together. SocialZen may deliberately use one SQLite connection to avoid driver deadlocks; all endpoint, publisher, export, notification, and analytics DB operations then serialize.
- Close query rows before provider HTTP calls or nested DB work.
- Do not equate four refresh workers with four-way DB throughput: provider calls can overlap while one connection serializes reads/writes.
- Count per-target DB operations around provider refresh and milestone evaluation. “Two metric reads plus provider persistence and notifications per successful target” is an N-dependent workload even when bounded workers prevent an unbounded fan-out.
- Review restart recovery semantics. Requeueing all `RUNNING` jobs is durable but can repeat provider calls unless target operations are idempotent.

## Payload and polling checks

- Measure bytes as well as latency for overview, enqueue, latest-job, and job-detail endpoints.
- Check whether job status responses include the full per-target `results_json` on every poll. A target cap bounds the damage but repeated transfer still grows linearly.
- Verify polling prevents overlapping requests, pauses while hidden, backs off/stops after repeated failures, and reloads overview only once after terminal completion.
- Remember that the post-refresh overview reload repeats all unbounded-query, JSON, and O(n²) costs.

## Correctness checks

- Follow each DTO field end-to-end: SQL scan → aggregate map → final response DTO → TypeScript type → modal. Intermediate fields can be silently dropped in the final projection.
- Verify account identity is populated rather than initialized to empty placeholders.
- For multi-platform posts, define aggregation semantics explicitly. Summing target metrics while collapsing one target’s unavailable reason to post level can produce contradictory output.
- Preserve nullable provider metrics. Do not turn missing/unsupported values into zero.
- Validate deep links where selecting a target changes the platform filter and triggers a second overview load; the selected post may disappear from the filtered result.

## Benchmark recipe

Use a temporary database and non-production port. Start the real backend, authenticate with the seeded session, then capture at least five runs per read endpoint using curl’s `time_total`, HTTP status, and `size_download`. Benchmark refresh enqueue separately from provider execution.

Report the dataset size with every timing. Seed-data millisecond results only prove fixed overhead; they do not disprove scaling defects. If practical, generate representative 100/1,000/10,000-post fixtures and report p50/p95 plus payload bytes.

## Test and log evidence

- Run focused analytics/refresh tests separately from the full suite so unrelated failures do not obscure domain evidence.
- Report both results exactly: focused pass count/time and full-suite failures with whether they are analytics-related.
- Search application/service logs for analytics failures, provider failures, `SQLITE_BUSY`, lock errors, and job-loop errors. “No matching repository log files” is not proof production had no failures.
- Never benchmark an unknown listener. Confirm the process/routes are the SocialZen backend; a quick 404 on the expected routes means the target is unsuitable.

## Read-only audit output

Return prioritized findings with exact file/line anchors, measured timings and bytes, dataset cardinality, test commands/results, log availability, and explicit limitations. State that no files were changed and distinguish pre-existing working-tree changes from audit activity.
