# Notification event delivery and click routing

Use this when Komuna notifications appear in tests or settings but not in the notification bell, or when notification rows are not actionable.

## Trace the serving stack first

- Confirm which backend is current. In the present architecture, `api/v1` (Go + SQLite) serves the React app; `apps/api` is historical and changing it does not fix production behavior.
- Trace the real event transition, not merely the notification service. For payments, create the notification in the canonical paid finalizer used by webhook and recovery paths.
- Insert payment notification in the same transaction and behind the same idempotent finalization guard as fulfillment. A duplicate provider callback must not create a duplicate notification.

## Event coverage

- Immediate/invitation join: notify the joining member.
- Approval-required join: acknowledge the requester and notify active program admins with an approvals link.
- Approval/denial: notify the requester after the decision succeeds.
- Voucher expiry and session reminders: ensure a scheduler actually starts, runs immediately, repeats, respects preferences, and inserts in-app rows (not only email/push-labelled rows).
- Keep preference event names identical across scheduler, API allowlist/defaults, frontend type/order, translations, and tests.

## Action URL contract

- Expose a dedicated `action_url` in the notification DTO; do not make the frontend infer destinations or navigate to `/`.
- For backward compatibility, parse legacy structured JSON bodies for message and action URL, while returning a plain display body.
- Accept only safe same-origin relative paths: must begin with one `/`, reject `/`, `//`, schemes/hosts, and backslashes. Fall back to `/notifications` when no valid event route exists.
- Map event classes to existing real routes: payments/vouchers → wallet; bookings → member bookings; joins → program; pending admin approval → program approvals; reminders → program sessions.
- Both dropdown and full-page rows should use the DTO URL and mark unread notifications for the authenticated owner only.

## Verification

1. Focused backend tests: duplicate paid callbacks produce one visible actionable row; public/invitation/pending joins and decisions notify correct recipients; unsafe URLs fall back safely; expiry/reminders are idempotent and preference-gated.
2. Focused frontend tests: actual rendered links have the expected href and clicking marks unread.
3. Run build and broader suites, reporting baseline failures separately from focused feature evidence.
4. For preview, use an isolated copied database and separate API process/port. Inject both preview router basename and preview API base in an explicit Nginx location. Verify root, deep route, JS/CSS MIME, and production asset hash remains unchanged.
