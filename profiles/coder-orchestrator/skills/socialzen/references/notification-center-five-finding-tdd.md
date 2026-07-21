# Notification Center Five-Finding TDD Pattern

Use this when a Notification Center review identifies the related correctness gaps below.

## Strict RED → GREEN sequence

For each finding, add and run one focused regression first. Confirm it fails for the intended missing behavior before editing production code. Apply the minimum fix, rerun the focused test, then move to the next finding.

## Durable preference suppression

A disabled publishing preference must permanently account for the committed target event. Otherwise, enabling the preference later lets restart reconciliation resurrect an event that was intentionally suppressed.

- Persist a processed-event marker keyed by user and stable target event key.
- Record whether the event was delivered or suppressed only after preference evaluation succeeds.
- Make both direct queueing and restart reconciliation consult the marker.
- Regression: suppress, flush, enable preference, reconcile and queue the same item, then assert no pending batch and no notification.

## Durable subscription delivery

A committed payment or plan transition must not depend on a best-effort notification call. Persist the event before attempting delivery.

- Write payment and plan-transition payloads to a deduplicated outbox after the subscription mutation commits.
- Materialize and close outbox rows before delivery because production SQLite has one connection.
- Mark an outbox row delivered only after notification delivery succeeds.
- Retry pending rows from startup/periodic notification maintenance.
- Regression: make notification delivery unavailable after the subscription commit, assert the outbox remains pending, restore delivery, reconcile, and assert it clears exactly once.

## Active unread badge semantics

The Bell count represents active, unarchived unread notifications. Reading archived history must not change that count.

- Archived mark-all-read may update archived rows, but emits no active unread delta.
- Opening an archived unread detail may mark it read, but emits no active unread delta.
- Archiving an active unread item decrements; unarchiving an unread item increments.
- Regression tests should listen to the shared unread event and assert no event for archived reads.

## Structural deep-link allowlisting

Prefix checks are insufficient: they can admit unknown descendants, encoded separators, or encoded traversal.

- Parse as a relative URL and reject scheme/host, protocol-relative values, backslashes, control characters, and non-canonical paths.
- Unescape and require the decoded path to equal the parser's canonical path; reject encoded path manipulation.
- Match explicit route shapes and permitted query-bearing leaf routes, not arbitrary prefix descendants.
- Test allowed routes alongside `/app/admin`, traversal, encoded traversal, encoded separators, and extra unsupported descendants.

## Maintenance cadence separation

Token-expiry warnings are account maintenance, not publishing work.

- Run once at startup and on a dedicated maintenance ticker (hourly is sufficient for a seven-day warning window).
- Keep publishing reconciliation/flush in the publishing cycle.
- Keep provider scans fully materialized before notification delivery.

## Fresh verification rule

Generated frontend output is stale after any source edit. At the end, run the exact requested package-manager command when possible (for example `pnpm run build`), not merely an equivalent command from earlier in the session. Also run focused backend tests, focused frontend tests, typecheck, backend build, and `git diff --check`. Report full-suite failures separately only when they are demonstrably unrelated; never let an earlier pass stand in for a fresh post-edit check.
