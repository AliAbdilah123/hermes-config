# Analytics Review Completion Audit

Use this after approval of a SocialZen analytics review or plan, especially when an earlier implementation covered only the most visible items.

## Completion rule

Do not treat a successful focused patch as completion of the review. Re-read every numbered finding and verify the actual backend → DTO → frontend → export path before reporting implementation complete. Build success and bundle markers do not prove semantic parity.

## Required audit matrix

1. **Canonical ranking**
   - One deterministic backend engagement/rank contract drives Top 3 chart, Top Posts table, Best Post, Highest Engagement, and PDF.
   - Check hardcoded limits independently; a chart capped at 3 does not mean the table or PDF is capped.

2. **Media propagation and rendering**
   - Select primary ordered `post_media`, fall back to `posts.media_thumbnail`, and serialize media type.
   - Verify every consumer uses video-aware rendering; a valid MP4 URL rendered through `<img>` is still broken.

3. **Insight cards**
   - Render all cards even with sparse data, using disabled `Not enough data` states.
   - Whole cards must be accessible controls when a referenced post exists.
   - Use a user-understandable section title and explanatory subtitle; internal product-analysis labels may confuse users.

4. **Unavailable is not zero**
   - Trace nullable metrics through overview summaries/cards, trend buckets/tooltips, table, post detail, PDF, sorting, and frontend fallbacks.
   - If an aggregate has no measured values, return/render unavailable rather than initializing it to zero.
   - Show controlled reasons only when supported by evidence; do not guess.

5. **Trend contract**
   - Backend trend buckets are the source of truth, grouped by publication date in the configured timezone.
   - Verify ISO-week Monday across year boundaries.
   - Remove or repair frontend fallbacks that silently reintroduce UTC grouping or null-to-zero coercion.

6. **Refresh UX and API contract**
   - Render a responsive summary card with Checked destinations, Fully refreshed, Partially refreshed, and Failed.
   - Expand details by human-readable destination/account, with refreshed metrics, unavailable metrics, controlled reason, and only relevant reconnect/retry action.
   - Never render target IDs, raw provider payloads, tokens, or stack traces.
   - If frontend sends `account_id`, prove backend decodes, validates, and scopes refresh and `lastUpdated` consistently.
   - Preserve the last successful values while reporting partial/failure outcomes.

7. **Configured timezone and export parity**
   - Posting-day/time insights use and display the configured user timezone, not an implicit browser timezone.
   - PDF follows the same Top 3, canonical ranking, and unavailable formatting as the UI.

## Delivery sequence

1. Convert every review item into an explicit checklist.
2. Add failing tests for each missing behavior before production edits.
3. Implement the smallest coherent contract changes.
4. Run focused backend/frontend tests, typecheck, and production builds.
5. Visually inspect deployed desktop and mobile states, including refresh partial/failure and sparse/no-data states.
6. Verify public asset content type and distinctive markers.
7. Inspect the final diff against the checklist, then commit/push only the analytics allowlist.
8. Report complete only when every checklist item is verified; otherwise say which items remain and keep working when implementation was authorized.

## Pitfall

A worker may finish one approved slice (for example ranking/thumbnails or the refresh card) and commit it while other review items remain. Never answer repeated “is it implemented?” prompts with progress prose alone. Inspect the repository state, reconcile it against the full review, and continue the authorized implementation until the complete review is delivered or a real blocker is identified.
