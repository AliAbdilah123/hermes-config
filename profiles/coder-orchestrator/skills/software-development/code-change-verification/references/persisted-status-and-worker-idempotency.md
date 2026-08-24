# Persisted status hydration and scheduled-worker idempotency

Use this reference for database-backed status controls (outcomes, preferences, workflow state) and digest/notification workers.

## Persisted status UI contract

A successful mutation plus a persisted database row is not sufficient when the UI initializes to a hard-coded default after reload.

Verification sequence:

1. Save the status through the authenticated mutation endpoint.
2. Restart the exact built server against the same temporary database.
3. Retrieve the current user's saved status through an authorized read endpoint.
4. Open the exact browser route and assert the control hydrates to that status.
5. Reload the page and assert the same value again.
6. Verify a member with no saved row gets an intentional empty/default response (commonly `404`), while a non-member gets `403`.

If only a `PUT` endpoint exists, add the smallest authorized `GET` needed to hydrate the control. Keep each participant's status scoped by both resource ID and reporter/user ID; do not leak another participant's private outcome.

## Scheduled worker idempotency

Unit tests with an injectable failing sender prove retry semantics, but also exercise the real worker command deterministically:

1. Bootstrap a fresh temporary database using the real migrations.
2. Insert one active, opted-in user and one old unread notification.
3. Run the exact worker command at a fixed UTC timestamp.
4. Require exactly one delivery and a `sent` ledger row with one attempt.
5. Run again at the same timestamp and require zero deliveries.
6. Require `PRAGMA integrity_check = ok`.

For SQLite with `MaxOpenConns(1)`, consume and close candidate rows before inserting/updating delivery ledger rows. Do not raise the connection limit to hide a read-then-write deadlock.

## Harness discipline

Keep browser scripts, development OTPs, temporary databases, and worker logs outside the repository. If a combined shell payload is rejected or too opaque, split setup, browser proof, and worker proof into separate commands; preserve each evidence boundary rather than weakening the verification.
