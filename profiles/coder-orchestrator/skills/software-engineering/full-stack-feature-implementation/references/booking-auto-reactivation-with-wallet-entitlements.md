# Booking auto-reactivation with retained wallet entitlements

Use when a user left a program, still owns valid wallet benefits, and booking incorrectly reports a ban.

## Diagnose

1. Trace membership lookup before entitlement lookup.
2. A query constrained to `status='active'` collapses inactive, missing, and banned memberships into the same outcome.
3. Inspect HTTP error translation separately: mapping generic `not_member` to `member_banned` creates a false-ban modal.
4. Confirm vouchers/subscriptions remain attached to the original program-member row after leaving.

## Safe transaction

- Load the existing membership and status without requiring active status.
- Keep `banned` as an explicit blocking outcome; keep a missing membership distinct.
- For inactive/left members, validate the session and usable entitlement before reactivation.
- In one transaction: consume or reference the entitlement, create the claim, reactivate the existing membership, increment capacity, write audit data, commit.
- Never reactivate before entitlement validation; failed booking must not silently rejoin a user.

## Regression cases

- Inactive + valid wallet entitlement: booking succeeds, membership becomes active, exactly one claim exists.
- Banned + valid entitlement: forbidden and still banned.
- Missing membership: non-ban `not_member` response.
- Active member behavior remains unchanged.
- UI success navigates to the canonical bookings route.

## Deployment-staleness check

When source and regression tests already contain the expected fix but the live site still shows the old behavior, treat deployment freshness as the leading hypothesis before changing code again.

1. Compare the fix commit timestamp with the running API binary mtime and process start time.
2. Inspect the service's effective `ExecStart`, `WorkingDirectory`, environment file, PID, and listening address; rebuild the exact binary path the service executes.
3. Restart the service, then wait for the socket/readiness signal before probing health. A restart can report `active` a moment before the listener is ready.
4. Build the frontend, publish `dist/` to the actual nginx document root, and verify public HTML references the new hashed bundle.
5. Probe both local and public health endpoints. Do not report deployment success from source tests alone.
6. Preserve unrelated dirty work by scoping status and diff checks to files and generated artifacts involved in the fix.

A stale binary or frontend bundle is a deployment defect, not evidence that the implemented logic is wrong. Avoid adding a second code fix until the deployed artifact has been proven current.

## Focused ad-hoc verification

If repository-wide suites have unrelated failures, create an OS-safe script with `mktemp /tmp/hermes-verify-<topic>-XXXXXX.sh`, run focused backend tests, focused UI tests, and the production frontend build, then remove it. Report this as ad-hoc verification rather than claiming the full suite is green.
