# Komuna website notification trigger wiring

Use this when implementing website/in-app notifications in Komuna's TypeScript API.

## Key distinction

Komuna has two notification paths that are easy to confuse:

- `notifier.enqueue(...)` / queue events: backend/event delivery path, often internal or email/worker-oriented.
- `notificationService.createNotification(...)` / `notificationCreator.createNotification(...)`: creates visible website/in-app notification rows.

When the user asks what triggers notifications "in the website", inspect actual `createNotification` calls, not only queue `enqueue` events.

## Existing integration pattern

- Approval flows accept an optional `NotificationCreator` dependency from `services/approvals.ts`.
- Route factories can wrap `createDrizzleNotificationService(...).createNotification(...)` and cast `eventType` to `NotificationEventType` before passing it into services.
- Keep notification failures non-blocking: wrap visible notification creation in `try/catch`, log, and do not fail the primary domain action.
- Preserve `metadata` and `actionUrl` passthrough in the `NotificationCreator` shape; otherwise website rows lose context and deep links.

## Common trigger mappings

- Join request approved/rejected: create visible notification for `programMember.userId`; use `approval_status` unless/until a dedicated event type is added.
- Booking approval/rejection: existing pattern uses `approval_status` for the member.
- Session activated/deactivated: queue currently uses `claim.claimantId` (program-member id), but visible website notifications need the actual user id. Join `programMembers` when listing active claims or otherwise resolve `claimantUserId`.
- Session deactivated/cancelled: reuse `booking_cancelled` or add a dedicated event type if preferences/UI are updated; include cancellation reason and session/claim metadata.

## Verification

- Add service tests asserting `notificationCreator.createNotification` calls, not just `notifier.enqueue` calls.
- Run targeted Vitest files first, e.g. notification-specific approval/session service tests.
- If the full test suite has broad unrelated middleware/type failures, report them separately and do not treat them as evidence the notification wiring failed.
