# Provider-safe analytics implementation

Use this when SocialZen analytics must support Instagram, Facebook, Threads, or cross-platform posts without metric overwrites.

## Data model

Store current analytics by publishing target, not on the parent post:

```sql
CREATE TABLE IF NOT EXISTS post_target_metrics (
  post_target_id TEXT PRIMARY KEY REFERENCES post_targets(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  likes INTEGER,
  comments INTEGER,
  reach INTEGER,
  impressions INTEGER,
  saves INTEGER,
  shares INTEGER,
  views INTEGER,
  plays INTEGER,
  captured_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

Keep unsupported/unavailable metrics nullable. `NULL` means unavailable; `0` means the provider measured zero. Do not use `COALESCE(metric,0)` at the analytics query boundary if capability/availability matters.

For legacy shared `posts` metrics, backfill only when a post has exactly one target. Multi-target legacy values are ambiguous and must begin fresh rather than being attributed to an arbitrary platform. Add schema/backfill changes to both `db.go` test migration and production `internal/models/models.go::Migrate()`.

## Provider refresh rules

- Iterate published `post_targets`, not parent posts.
- Pass the exact `post_target_id` into each provider refresher. Passing only `post_id` can repeatedly refresh whichever same-platform target happens to sort newest while falsely reporting every target successful.
- Provider lookup must resolve credentials and provider post ID from that exact target.
- Collect target rows and close the cursor before API calls or nested DB queries because production SQLite uses one connection.
- Return provider/API and malformed-response failures as failures. Never persist zeros and report success when Instagram insights were absent or failed to decode.
- Refresh response should include per-target results plus aggregate `success`, `partial_success`, or `failed`, and the persisted latest successful update timestamp.

## Overview query semantics

- Validate `platform`, `account_id`, `from`, and `to` at the backend boundary.
- Treat date inputs as inclusive local calendar dates and query with `[from 00:00, day-after-to 00:00)` after timezone conversion.
- Avoid duration-based day counts across DST. Daily is up to 90 inclusive calendar days; weekly starts above 90.
- Handle null publication timestamps explicitly instead of scanning SQL NULL into Go strings.
- In single-platform mode, use target metrics for that platform.
- In All Platforms mode, sum target activity but group the post DTO by parent post ID. Otherwise post count, averages, comparisons, and What Worked are duplicated once per target.
- Label All Platforms as summed platform activity, not unique people.

## Response contract

Keep backend/frontend keys aligned. If the backend emits `trendBuckets`, the frontend type and caller must consume `trendBuckets`—do not silently fall back to rebuilding per-post trends.

Each trend bucket should include the fields the chart reads, including derived `engagement = likes + comments + supported saves + shares`. Preserve daily/weekly granularity returned by the backend.

Post DTOs should include:

- parent post ID and caption
- content type
- published timestamp
- target/platform data
- nullable supported metrics
- engagement rate
- nullable `vsAverage` and `comparisonAvailable`

Calculate `vsAverage` against the other eligible posts in the same filtered scope. One-post or zero-reach scopes render unavailable (`—`), not `0%`.

## UX requirements

- Keep stale analytics visible during background refresh.
- Distinguish initial loading, empty filtered range, load error, refresh partial/failure, and export error.
- Render missing `lastUpdated` as `Never`/unavailable, never epoch time.
- Drive cards, chart toggles, tooltips, and reports from one platform capability map.
- “What Worked” should include best post, highest engagement, best content type, and best posting day/time with sample count. Use deterministic tie-breaks.
- “Create a post like this” should use the real New Post route (`/app/posts/new`) and only prefill fields the create flow actually consumes.
- PDF titles should be `<Platform> Analytics Report` or `Cross-platform Analytics Report`.

## Verification

1. Add tests first for per-target isolation, nullable unsupported metrics, date boundaries, All Platforms grouping, comparisons, trend engagement, weekly cutoff, and insight sample counts.
2. Run targeted Go analytics/provider tests and build the backend.
3. Run focused Vitest, TypeScript typecheck, and frontend production build.
4. Before deployment, independently review the backend/frontend contract; targeted tests can miss mismatched response keys.
5. Back up SQLite, deploy, verify `post_target_metrics` exists, service health is active, public page returns 200, analytics chunk is JavaScript, and the deployed bundle contains a distinctive new UI marker.

## Common pitfalls

- A provider-safe table alone does not guarantee provider-safe writes; exact target identity must flow through every refresher.
- One row per target is correct for storage but wrong for an All Platforms post list unless grouped back to the parent post.
- SQL null-to-zero coercion defeats capability-aware UI.
- Backend aggregation is wasted if frontend response keys drift and trigger a fallback.
- A computed insight is not delivered until its component actually renders it.
- Add legacy backfill only after `post_targets` exists and has been backfilled in the production migration order.
