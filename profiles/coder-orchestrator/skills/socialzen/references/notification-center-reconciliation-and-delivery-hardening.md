# Notification Center Reconciliation and Delivery Hardening

Use this after a completion audit finds that notification helpers exist but delivery is not durable or UI state drifts.

## Publishing: distinguish delivered, suppressed, and unseen

A preference check that simply returns `delivered=false` is not sufficient. Finalized `post_targets` remain eligible for restart reconciliation, so an event suppressed today can be backfilled after the user enables that preference later.

- Persist an item-level processed marker keyed by `(user_id, stable_event_key)`.
- Record outcome (`delivered` or `suppressed`) only after notification delivery/preference evaluation succeeds.
- Reconciliation must consult processed markers before queueing finalized targets.
- Keep notification dedupe keys too: notification uniqueness and source-event processing are separate concerns.
- Do not impose a small fixed reconciliation limit. Either page through every candidate with a durable cursor or process the complete set; a single `LIMIT 100` silently strands older events.

Regression shapes:
1. Disable publishing preference, finalize and flush an event, re-enable preference, reconcile, assert no notification appears.
2. Insert 101 finalized targets, reconcile with the legacy limit argument, assert all 101 are considered.

## Subscription events: durable outbox at the committed boundary

Calling a notification helper after a subscription upsert is correctly ordered but still lossy if errors are ignored.

- At the same domain completion boundary, persist stable serialized payment/plan-transition events into a durable outbox.
- Dedupe with the provider event identity plus transition identity (for example provider reference + payment, or old plan + new plan).
- Reconcile pending outbox rows immediately as best effort and again from scheduled maintenance.
- Mark an outbox row delivered only after the notification producer succeeds.
- Materialize and close SQLite rows before delivery/update queries because production uses one connection.
- Test delivery failure leaves a pending row, then retry succeeds once without duplicate notification.

## Archived unread badge semantics

The global badge counts active, unarchived unread notifications only.

- Marking an archived notification read: badge delta `0`.
- Mark-all-read with `archived=true`: badge delta `0`.
- Archiving an unread active notification: `-1`.
- Unarchiving an unread archived notification: `+1`.
- Deleting an unread active notification: `-1`; deleting an archived notification: `0`.
- Dispatch badge synchronization only after the mutation succeeds. Surface mutation failures visibly and leave local state/count unchanged.

Cover Bell, list, and detail routes; polling is reconciliation, not the primary mutation UX.

## Deep-link allowlisting

Prefix checks such as `/app/` plus rejection of literal `..` are bypassable.

1. Parse as a relative URL; reject scheme, host, backslashes, CR, and LF.
2. Reject encoded-path ambiguity (`RawPath`) and percent-decoding errors.
3. Decode and normalize the path; reject if cleaning changes it.
4. Compare against explicit route shapes and bounded dynamic-segment counts.
5. Apply the same sanitizer on insertion and response serialization.

Regression inputs include `/app/admin`, `/app/posts/../../admin`, `/app/posts/%2e%2e/admin`, encoded separators, protocol-relative URLs, and unsupported descendants.

## Token-expiry maintenance

Token-expiry producers must cover Instagram, Facebook, and Threads and dedupe by provider/account/expiry timestamp. Run them from startup plus an hourly maintenance ticker rather than coupling three account scans to the minute-level publishing cycle. Prefer SQL predicates bounded by the warning window as account volume grows.

## Verification and release gate

- Add schema in both `internal/models.Migrate()` and legacy/test `app.migrate()`.
- Run focused notification and subscription tests, backend build, frontend notification tests, typecheck, and production build.
- Independently review the diff against every audit row before commit.
- Treat unrelated full-suite failures separately, but never hide them.
- After deploy verify service health, new tables, public SPA asset identity/content type, and authenticated notification mutations when credentials are available.
