# Analytics background-job TDD handoff

Use when converting SocialZen analytics refresh from a synchronous request into a durable SQLite background job.

## Delivery discipline

- Treat the approved plan's acceptance checklist as the definition of done. A queue table, `202`, ticker, and polling UI are only a vertical slice—not end-to-end completion.
- Keep a numbered checklist for migrations, enqueue/read authorization, runner bounds, terminal metadata, unavailable tombstones, notifications, lifecycle wiring, typed client, polling/recovery, and result/accessibility UI.
- Execute one RED → GREEN cycle per checklist row. Preserve the actual RED output before production edits.
- When the API contract intentionally changes from synchronous `200` to queued `202`, update or replace every old synchronous test in the same cycle. A failing old concurrency test is not “unrelated”; move its assertions to runner execution and retain concurrency/order coverage.
- Do not route the background runner through the old HTTP handler or synthesize a user session. Extract a request-independent worker taking durable job/user/scope data and a runner context. HTTP authentication belongs only at enqueue/read boundaries.
- The runner must select at most 200 newest published targets, close rows before provider I/O, skip persisted `UNAVAILABLE` metrics, use at most four target workers, and retain deterministic result order.
- Do not rely on stringifying an `io.Reader` for provider-error classification. Classify actual errors (or a minimal structured Meta error) and test permanent vs retryable boundaries.
- Wire terminal Notification Center receipts and reconciliation before calling the feature complete. Dedupe by job ID + terminal status and never persist raw provider errors.
- Frontend polling must implement remount recovery, scope/unmount stale-response guards, visibility/focus behavior, bounded poll-error handling with `Check status`, and exactly one background overview reload for every terminal state.

## Completion pitfalls discovered during handoff

- Preserve availability metadata through every DTO projection. Adding `unavailableReason` in `analyticsMaps` is insufficient if `analyticsPosts` rebuilds the public post map and omits it; assert at the final API DTO boundary.
- Background-job changes can expose old synchronous copy assertions outside the new component test. Search analytics tests for superseded labels such as `Analytics refresh completed with some issues` / `Partial Success` and update tests that cover the changed contract to the exact terminal labels.
- Analytics drill-down must tolerate sparse DTO fields produced while data is unavailable or stale: use optional target access and guard missing/invalid `publishedAt` before date formatting. Keep a focused sparse-post render test.
- After the final edit, rerun a fresh canonical frontend build even when an earlier typecheck/build passed; verification produced before the last patch is stale evidence.

## Verification and reporting

Run focused commands directly (the repository-wide pnpm test script may discover all tests despite file arguments), then canonical full gates:

```bash
cd apps/backend-go
go test . -run 'AnalyticsRefresh|AnalyticsOverview'
go test ./internal/comments ./internal/facebook ./internal/threads ./internal/notifications
go test ./...
go build ./...

cd ../frontend
pnpm exec vitest run src/lib/analytics.test.ts src/pages/analytics/AnalyticsPage.test.tsx src/components/analytics/RefreshResultCard.test.tsx
pnpm test
pnpm typecheck
pnpm build
```

Before reporting completion:

- Any failure in a pre-existing test that directly covers the changed refresh contract is in scope and must be migrated/fixed.
- Separate genuinely unrelated full-suite failures from feature failures with exact names and evidence.
- If acceptance rows remain missing, report the implementation as partial; do not say “implemented end-to-end.”
- Never deploy, commit, or push when the instruction is to leave worktree changes for parent verification.
