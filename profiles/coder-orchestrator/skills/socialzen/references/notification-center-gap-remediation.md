# Notification Center Gap Remediation

Use this after a completion audit identifies multiple gaps in an already-shipped Notification Center.

## Do not treat one implementation pass as completion

Convert every reported gap into a tracked acceptance row and keep it open until there is direct evidence. A worker that fixes four of ten items has produced a useful partial pass, not a completed feature. Re-dispatch or continue directly for every uncertified row before commit/deploy.

## High-value regression shapes

- **Publishing reconciliation:** seed more rows than the old batch size (for example 101 against a 100-row limit) and assert every finalized target is reconciled. Prefer durable pagination/checkpointing or exhaustive bounded batches; never make a one-shot fixed limit the correctness boundary.
- **Preference suppression:** prove a publishing event suppressed when the preference is disabled cannot be created later by restart reconciliation. Record/advance durable reconciliation state even when delivery is suppressed; preference checks must not leave the event looking unprocessed.
- **Archived mark-all-read:** pass the current archived filter from frontend to API and include it in the repository predicate. Test active and archived rows together so the wrong population cannot be marked accidentally.
- **Token expiry:** schedule a producer that scans Instagram, Facebook, and Threads accounts. Dedupe with platform/account identity + exact expiry timestamp + warning window, so token renewal creates a new warning lifecycle while repeated scans remain idempotent.
- **Analytics cooldown:** test two threshold crossings for the same exact `post_target_id`/metric inside and outside six hours. Cooldown identity must not collapse sibling targets or unrelated metrics.
- **Exact analytics target:** carry `post_target_id` through stored details and deep links/query selection. Test two same-platform targets under one parent post and assert the intended target is selected.
- **Badge reconciliation:** use one shared notification-state invalidation/event mechanism after read, mark-all-read, archive, unarchive, and delete. Update optimistically only when rollback/error behavior is defined; otherwise mutate then refresh count immediately. Polling is fallback, not mutation consistency.
- **Mutation errors:** every Bell/List/Detail mutation must catch failure, preserve/restore local state, and show an accessible visible error. Silent catches are not acceptable completion evidence.
- **Subscription events:** a notification event case/helper without a caller is Partial. Test the real plan mutation/webhook completion path and stable provider-event or transition dedupe.
- **Deep links:** validate at insertion and response boundaries with an explicit internal-route allowlist; reject traversal, protocol-relative URLs, unknown app routes, and non-HTTPS external links. Frontend filtering alone is insufficient.

## Producer-boundary rule

Insert notifications only after the source transaction/mutation has committed. For SQLite configured with one connection, fully materialize and close query rows before notification repository calls. Tests should prove failures before commit produce no notification and retries remain idempotent.

## Verification and handoff

1. Capture the pre-change working tree and preserve unrelated files.
2. For each gap, record the RED failure and GREEN command result.
3. Run focused notification suites, then full Go/frontend suites, typecheck, and builds; classify baseline failures separately.
4. Review the actual diff and `git diff --check` yourself after delegated work—subagent summaries are claims, not evidence.
5. Do not commit/deploy until all non-conditional audit rows are implemented or explicitly reported as remaining blockers.
6. After deployment, perform authenticated production list/count/detail and mutation smoke tests; health and asset checks alone are insufficient.
