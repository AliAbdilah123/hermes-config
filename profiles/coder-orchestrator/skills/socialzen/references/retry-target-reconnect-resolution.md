# Save & Retry target resolution after social-account reconnect

When fixing failed-post retry for disconnected/reconnected accounts, keep target migration tied to the provider's stable external account/page ID, not the app's internal row ID.

## Problem shape

A failed `post_targets.account_id` can point at an internal account row that was later deleted or marked `DISCONNECTED`. If the user reconnects the same Facebook Page / Instagram Business Account, the app may create a new internal row for the same external provider ID. Retrying against the stale internal ID fails even though the same external account is active again.

## Durable fix pattern

1. Store a stable external ID on each `post_targets` row, e.g. `provider_account_id`:
   - Instagram: `instagram_accounts.ig_user_id`
   - Facebook: `facebook_pages.page_id`
   - Threads: `threads_accounts.threads_user_id`
2. On post creation, populate `provider_account_id` from the selected internal account/page.
3. In migrations, add the column to both migration paths:
   - production: `internal/models.Migrate()`
   - tests/legacy: `db.go`'s `(a *app) migrate()`
4. Backfill existing rows by joining `post_targets.account_id` to provider account tables while the old row still exists.
5. Before `patchPost` requeues a failed post, resolve every failed target by **same platform + same provider_account_id**:
   - if an active row exists, update `post_targets.account_id` to that current active internal row and keep `provider_account_id` stable;
   - if no active same-external row exists, do not requeue; return a clear message asking the user to reconnect that provider or remove the target.
6. Never auto-switch to a different external account/page just because it is active.

## Regression tests to add

Use backend tests around `patchPost` / retry requeue:

- Disconnect/reconnect same Instagram/Facebook external account -> target `account_id` updates to active row and status becomes `SCHEDULED`.
- Disconnect/reconnect a different external account -> retry returns a clear reconnect/remove-target error and the failed target stays `FAILED`.
- Multiple reconnect rows for the same external account -> choose the current `ACTIVE` row, not old disconnected rows.

## Pitfalls

- If an old internal account row was physically deleted before `provider_account_id` existed, the app may not be able to infer the stable external ID for that historical target. The backfill only works while the old row or a previously stored provider ID is available.
- Keep SQLite single-connection rules: read target rows into memory and close `Rows` before nested lookup/update queries.
- `go test ./...` in SocialZen may have unrelated root-package failures; still run targeted package tests and `go build` for the changed backend path, and report unrelated failures explicitly.
