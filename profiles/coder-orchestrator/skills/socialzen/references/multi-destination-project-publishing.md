# Multi-destination Project publishing

Use this reference when extending SocialZen’s publishing workflow from one post to multiple Instagram/Facebook destinations.

## Architectural boundary

- Treat the existing parent `posts` record as the shared Project/workspace unless a proven persistence requirement cannot fit it.
- Keep `post_targets` as destination-level execution and history records. Do not create a second publisher, queue, analytics model, or details route.
- Preserve existing URLs and represent old records as legacy Projects.
- Shared caption, media, schedule, hashtags, and settings belong to the parent. Destination records contain provider/account identity, execution state, provider result, and destination-scoped errors.

## Transaction, snapshot, and validation order

1. Resolve and validate every requested destination before Review: ownership, active/token state, permissions, provider capability, caption limit, and media compatibility.
2. Return stable destination-scoped validation results. A global caption violation blocks submission; destination-specific media incompatibility excludes only that destination.
3. Persist an immutable, expiring preflight snapshot of the reviewed destination identities and publishing configuration. Return its opaque ID to the composer and freeze the reviewed payload; leaving Review invalidates the local reviewed payload.
4. At Publish, revalidate current provider/account state and compare the submitted targets/configuration to the stored snapshot. Never silently rewrite destinations. Reject missing, expired, consumed, or changed snapshots with a stable stale-preflight error that sends the user back through validation and Review.
5. In one database transaction create/update the parent, media links, targets, destination-based quota reservation, and single-use snapshot consumption. Check every write and rollback on any error.
6. Enqueue only after the transaction commits. Never expose an ID for a rolled-back Project.

Add focused tests that (a) deliberately fail a late target/media/quota write and assert that no parent, media, target, reservation, or snapshot consumption survived, and (b) mutate an account after Review and assert Publish rejects the stale snapshot without persisting a Project.

## Idempotency, recovery, retry, and cancellation invariants

- Give every destination publication a deterministic idempotency key tied to the immutable Project/version and destination identity; persist it before provider execution.
- Provider calls, manual retry, and restart recovery reuse that key and preserve any provider ID/permalink already recorded.
- Manual retry queries only failed targets. Recovery resumes unfinished targets and skips completed targets.
- A target with a successful provider record/permalink is an idempotency boundary: never recreate or repost it.
- Preserve successful targets during partial success and recompute the parent status from all target states.
- Cancel only pending/queued targets; retain completed, failed, analytics, provider records, and immutable publication history.
- Archiving changes workspace visibility/state, not publication history.

Test crash recovery at both boundaries: after provider success but before local completion persistence, and after one target completes while sibling targets remain unfinished. Assert repeated execution does not duplicate the successful provider publication.

## UI contract

Use the existing composer in this order: destinations → shared content → Review → publish. Support multiple accounts per provider and remember the last selection. Review must show destinations, schedule, media, caption, and compatibility results. Hide Threads and unsupported content options at every V1 entry point, not only in the composer. Reuse Project cards and Post Details rather than adding parallel screens.

## Delivery discipline

- Start by translating the approved contract into a behavior matrix and focused RED tests; implement coherent vertical slices rather than claiming the entire contract from broad terminology changes.
- When a user cannot see a newly implemented Project/cross-platform entry point after refresh, trace the complete serving chain before editing again: route source → tests/build → commit/upstream → domain redirect → exact Nginx `alias`/document root → public HTML entry hash → route lazy chunk → rendered authenticated UI. SocialZen may redirect `/` to a nested mount such as `/projects/socialzen/`; copying `dist/` to a nearby generic web root can leave production serving the old bundle even though local deployed files contain the new markers.
- For persistent feature discovery, verify all responsive entry points: desktop sidebar, mobile bottom navigation, Projects page header, and collection-empty CTA. Assert each navigates to `/app/posts/new`; then inspect the deployed route chunk and exercise the exact public authenticated route after a hard refresh. A source label, local deployed-file marker, HTTP 200, or entry-bundle hash alone is insufficient.
- Preserve dirty runtime databases and unrelated plans/docs. Record the baseline status and stage only explicit implementation paths.
- When the dirty worktree already contains a substantial partial implementation of the approved plan, inspect and continue that exact diff. Do not restart, revert, or create a parallel implementation; identify missing acceptance criteria and close only those gaps.
- If the user reiterates that an approved proposal must be implemented, treat that as evidence the prior delivery was incomplete—not as a request to merely rerun the same tests. Re-open the approved artifact, construct an explicit acceptance-criteria matrix, audit committed behavior against every row, and implement all missing rows before reporting again.
- Treat coding-agent completion as an untrusted handoff. Before committing, build an acceptance-criteria matrix from the approved plan and inspect the final diff, API routes, schema, queue behavior, and UI against every row. Do not infer that atomic creation, immutable runs, stale-snapshot confirmation, recovery, analytics scopes, lifecycle actions, or dual creation entry points are complete merely because representative code and focused tests exist.
- Preserve the explicit distinction between multi-platform Projects and regular single-platform Posts. Verify both entry buttons are visible on the requested responsive surfaces, each opens the correct mode, regular Post mode permits exactly one destination without cross-platform selection, and Project mode retains multi-account/multi-platform selection.
- Run focused backend tests and build, focused frontend tests and production build, then the broad suites. Run test, typecheck, and build as independent gates when collecting final evidence, so an unrelated test failure does not suppress valid typecheck/build results. If a chained command stops at tests, rerun the skipped build separately; never report it as having passed from the chained invocation.
- Classify broad-suite failures precisely as changed-feature regressions or pre-existing/unrelated failures. Prove that classification with fresh focused feature tests; do not infer it merely because a failing test name looks unrelated, and never report “complete” while acceptance criteria remain unverified.
- Treat provider-backed publishing as a separate release gate: implementation and local automated verification may be complete while commit, push, and production deployment remain blocked. Do not deploy until real connected Instagram Business and Facebook Page tests cover the supported media combinations and confirm per-target provider records, partial failure, and failed-only retry.
- Final results must distinguish implemented, focused automated verification, each broad gate, broad-suite blockers, commit/push status, deployment status, and real-provider verification still required.
