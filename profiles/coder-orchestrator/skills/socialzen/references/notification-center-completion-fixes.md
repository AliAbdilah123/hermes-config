# Notification Center Completion Fixes

Use this after a completion audit finds that the core Notification Center exists but producer and reconciliation boundaries are incomplete.

## Durable publishing reconciliation

- Never reconcile only a fixed newest batch (for example `LIMIT 100`); older finalized targets can be omitted forever.
- Reconcile the complete eligible set in bounded pages or process all materialized candidates. Under SocialZen's single SQLite connection, close each `Rows` cursor before notification repository work.
- Preference suppression must be durable: if a publishing event is suppressed when finalized, record a stable processed/suppressed marker or otherwise ensure later reconciliation cannot backfill it after the preference changes.
- Regression test with more rows than the former limit and assert every eligible target is accounted for exactly once.

## Token-expiry production

- Scan Instagram, Facebook, and Threads account stores—not just one provider.
- Produce warning events from a scheduled/startup maintenance boundary.
- Dedupe by provider + account identity + exact expiry timestamp + warning window so reconnect/token refresh naturally creates a new event while repeated scans do not.

## Subscription boundaries

- A `plan_changed` case in the notification service is not implementation unless a real caller exists.
- Emit payment and plan-transition notifications only after the subscription write reports success at the shared payment/webhook application boundary, not merely from one HTTP confirmation handler.
- Snapshot previous plan before the mutation and compare it with the committed plan afterward.
- Use provider event/external payment identity in dedupe keys; repeated callbacks must remain idempotent.
- Test the actual boundary twice and assert one payment event plus one transition event with `fromPlanId` and `toPlanId`.

## Archived Mark all read

- Carry the archived filter end-to-end: frontend request helper → query string → handler filter → repository SQL.
- `archived=true` must update archived rows only; active-view mark-all must not accidentally include archived history.

## Immediate badge reconciliation and mutation errors

- Keep one tiny browser event contract (for example an unread-count delta event) shared by Bell, list, and detail views.
- Dispatch only after successful mutations. Read/delete/archive active unread rows decrement; unarchiving an unread row increments; mark-all decrements by the backend's returned updated count.
- Clamp the Bell count at zero and retain polling/focus refresh as authoritative reconciliation.
- Every mutation path must catch failures, render an accessible visible error (`role="alert"`), preserve local state, and avoid navigation when marking read is required but failed.
- Test both success deltas and failure paths that emit no delta.

## Deep-link hardening

- Validate stored links server-side with an explicit set of allowed application route prefixes plus strict HTTPS rules for permitted external provider links.
- Reject traversal, protocol-relative URLs, unknown privileged routes, and malformed values; do not rely on a generic `/app/` prefix.
- Add table-driven allow/deny tests.

## Verification/reporting

Run focused notification/subscription Go tests, backend build, focused Bell/list/detail frontend tests, typecheck, and production build. Run full suites separately and classify unrelated baseline failures honestly. Do not claim all audit rows complete until actual callers, scheduler wiring, authenticated production mutations, and preference-suppression behavior are evidenced.
