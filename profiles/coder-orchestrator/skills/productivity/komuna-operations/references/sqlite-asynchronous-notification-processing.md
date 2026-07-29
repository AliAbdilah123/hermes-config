# SQLite asynchronous notification processing

Use for Komuna notification delivery and scheduled generation while the app remains a single Go + SQLite deployment.

## Boundary

- Create `in_app` notification rows synchronously so they are immediately visible and can participate in the triggering business transaction.
- Process non-in-app channels (`email`, `push`, `sms`) asynchronously.
- Schedule voucher-expiry and session-reminder generation asynchronously.
- Keep read/unread changes, preferences, and action-URL navigation synchronous.
- Product language: **asynchronous notification processing**. Implementation language: **SQLite-backed notification jobs** and **notification worker**.

## Minimal schema

Store jobs with:

- `kind`, JSON `payload`
- `status`: `queued | running | done | failed`
- `attempts`, `run_at`, `locked_at`, `last_error`
- unique `idempotency_key`
- creation/update timestamps

Use a claim index over `(status, run_at, locked_at)`.

## Processing rules

1. Enqueue non-in-app delivery with a unique key such as `notification:<recipient>:<event>:<channel>:<target>`.
2. Claim one eligible job atomically with one SQLite `UPDATE ... RETURNING`; never select and update separately.
3. Increment attempts and set `locked_at` while claiming.
4. On success, mark `done` and clear lock/error state.
5. On failure, save the error and requeue with exponential backoff; mark `failed` at the attempt ceiling.
6. Treat old `running` locks as abandoned and reclaim them after a fixed timeout.
7. Run one worker initially. Add Redis or a separate queue service only for multiple app instances or measured throughput pressure.
8. Job handlers must be idempotent because retries and stale-lock recovery can repeat execution.

## Scheduled generation

The scheduler should enqueue a generation job rather than perform notification scans inline. The worker runs the voucher-expiry and session-reminder generators. Give generation jobs a timestamp-based idempotency key so duplicate scheduler ticks do not duplicate work.

## Verification

Test these behaviors directly:

- in-app insertion is immediate while external delivery remains queued;
- duplicate enqueue produces one job;
- concurrent claims yield one claimant;
- stale `running` jobs are recovered;
- failures back off and eventually become `failed`;
- scheduled generation is idempotent and creates expected in-app rows/delivery jobs.

Run focused Go tests first, then `go vet ./...` and the broader suite. Report unrelated pre-existing suite failures separately rather than presenting them as feature failures.

## Preview operations

For an existing functional preview with an isolated API/database:

1. Confirm the preview worktree is clean before editing and preserve the shared production checkout even if it is dirty.
2. Build and test in the preview worktree only.
3. Restart the preview API process so backend-only changes actually reach the public preview; rebuilding the SPA is insufficient.
4. Confirm Nginx still routes the preview API prefix to the isolated API and that its `SQLITE_DB_PATH` points to the preview database.
5. Run `PRAGMA integrity_check` and inspect job states in that preview database.
6. Verify the public preview root/deep route, injected preview API base, authenticated notification flow when applicable, and production asset identity remains unchanged.
7. Commit and push the feature branch, but do not merge or deploy production before explicit approval.

A backend-only asynchronous-processing change may have no new visible UI. State that clearly: the existing notification actions remain the review surface while queue behavior is proven through API/database flow and focused tests.