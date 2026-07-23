# Deferred subscription renewal cancellation and entitlement recovery

Use this playbook when a wallet action labeled “Cancel renewal” currently disables subscription access immediately, or when an affected entitlement must be safely restored.

## Required behavior

- The first click opens an accessible confirmation dialog; it performs no API write.
- Explain the exact access end date/time and state that cancellation takes effect immediately after expiration.
- Confirmation schedules cancellation while keeping `status='active'`.
- Persist the scheduled end separately (for the Go+SQLite service, `cancel_at=expires_at`) and return it in the Wallet DTO.
- After confirmation, disable/relabel the action and show a status message that access remains active until expiry.
- Expiration processing may later transition due subscriptions to `cancelled`/`expired`; do not overload the confirmation request with immediate entitlement revocation.

## TDD boundary

1. UI test: click “Cancel renewal”; assert no POST occurred and dialog copy includes the formatted expiry.
2. Confirm; assert the POST occurs and success copy says access remains active until expiry.
3. API test: after cancellation request, assert `status` is still `active` and `cancel_at == expires_at`.
4. Run the targeted API and Wallet tests, then production builds.

## Recovering an accidentally cancelled entitlement

Treat the requested account/email as a lookup key, not proof of a unique row. Inspect all matching users, memberships, products, and subscriptions first. Identify the intended row by product/program and dates.

Before writing:

- Back up the configured SQLite database with a timestamped filename.
- Confirm the schema supports deferred cancellation; let normal app startup migrations add the column where practical.
- Use a guarded transaction such as `UPDATE ... SET status='active', cancel_at=NULL WHERE id=? AND status='cancelled'`.
- Check exactly one row changed; otherwise roll back/investigate.
- Read the row back with account, product, status, expiry, and `cancel_at`.

## Deployment verification

For Komuna’s split Go API/static SPA deployment, a pushed commit is not deployment. Build the API, restart its service, build the web app, sync `dist/` to the nginx root, then verify:

- service is active and local health responds;
- public root returns HTTP 200;
- deployed JS contains a distinctive confirmation-modal marker;
- recovered subscription remains active with the expected expiry;
- the feature commit is pushed.

Avoid touching unrelated dirty worktree files. Do not include a database backup or built binary in the feature commit.