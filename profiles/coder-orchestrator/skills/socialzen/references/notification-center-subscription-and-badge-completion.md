# Notification Center: Subscription Boundaries and Immediate Badge Sync

Use this when closing the final subscription producer or frontend mutation-state gaps in SocialZen's Notification Center.

## Subscription plan-change boundary

- Wire subscription notifications at the shared committed mutation function, not only at an HTTP return handler or webhook wrapper. SocialZen payment success can arrive through both the browser confirmation path and Xendit webhook; the shared subscription upsert is the reliable boundary.
- Read the previous `plan_id` before the upsert, perform the upsert, then emit only after it succeeds.
- Emit `payment_succeeded` for the provider event and emit `plan_changed` only when a non-empty previous plan differs from the new plan.
- Use stable provider-derived dedupe keys with distinct suffixes for payment and transition notifications. Repeated confirmation/webhook delivery must create one notification of each applicable type.
- Snapshot both `fromPlanId` and `toPlanId`; `planId` alone cannot explain a historical upgrade/downgrade.
- Avoid duplicate producer calls in outer handlers after moving delivery to the shared mutation boundary.

### TDD regression shape

1. Seed a user with an active old plan.
2. Call the real paid-external-ID mutation twice with the same provider event ID and a new plan.
3. RED should show no notification rows before wiring.
4. GREEN asserts exactly one `payment_succeeded` and one `plan_changed`, with old/new plan IDs in `details_json`.

## Frontend mutation errors and badge synchronization

- Every notification mutation must catch and visibly render its own actionable failure: mark read, mark all read, archive, unarchive, delete, and detail-page automatic read.
- Do not navigate away after a failed click-to-read mutation; retain the unread item and let the user retry.
- Reconcile UI state only after the API succeeds. Failed mutations must not remove rows, mark them read, or decrement the badge.
- Use one small window event carrying an unread `delta` so all mounted `NotificationBell` instances update immediately without waiting for the 30-second poll.
- Successful state transitions:
  - mark one read: `-1` if previously unread;
  - mark all read: negative API `updated` count;
  - archive active unread: `-1`;
  - unarchive unread: `+1`;
  - delete active unread: `-1`;
  - detail auto-read: `-1` only after success.
- Clamp badge state at zero. Polling remains authoritative reconciliation for cross-tab/server-side changes.

### Frontend TDD regression shape

- Force each mutation helper to reject and assert a visible `role="alert"`, unchanged row state, and no unread event.
- Resolve each mutation and assert immediate badge delta without advancing polling timers.
- Wrap manually dispatched custom events in React Testing Library `act(...)` to avoid stale assertions and update warnings.

## Verification

Run fresh checks after the final source edit:

```bash
cd apps/backend-go
go test ./internal/notifications ./internal/subscription ./internal/webhook
go build ./...

cd ../frontend
pnpm run build
```

Also run focused Vitest files for the bell, list, and detail page. If the repository package manager command is unavailable, report that exact blocker and run only an explicitly equivalent package script when allowed; do not represent the equivalent command as the requested command itself.
