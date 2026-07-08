# Pending downgrade subscription invoice reminder

When a paid user downgrades before the current plan period expires, Xendit can create/register an invoice while the active subscription should remain unchanged until payment succeeds. If no pending invoice state is stored, the UI cannot remind the user about the unpaid downgraded-subscription invoice.

## Durable fix pattern

1. Keep the current active subscription (`plan_id`, `current_period_end`) unchanged when creating a downgrade invoice.
2. Store pending downgrade invoice metadata on the active subscription row:
   - `pending_plan_id`
   - `pending_invoice_id`
   - `pending_payment_url`
   - `pending_invoice_amount`
   - `pending_created_at`
3. Expose `pendingPlanChange` from `SubscriptionData()` / `/api/subscription/status` so global layout UI can render a reminder before expiry.
4. Add actions:
   - `POST /api/subscription/continue` returns the saved `pending_payment_url` so the user can resume payment.
   - `POST /api/subscription/reject` clears all pending downgrade fields; it does not cancel/change the current active plan.
5. When payment success is confirmed (`applyPaidExternalID` / subscription upsert), clear all pending fields as part of activating the paid plan.
6. The global subscription banner should prioritize pending invoice reminders over expired-plan warnings.

## Migration checklist

- Update the `CREATE TABLE IF NOT EXISTS subscriptions` schema for fresh DBs.
- Add duplicate-column-tolerant `ALTER TABLE subscriptions ADD COLUMN ...` migrations for existing DBs.
- Verify live DB with `PRAGMA table_info(subscriptions)` after deploy.

## Regression shape

- Insert an active higher plan with future `current_period_end` and pending downgrade invoice fields.
- Assert `SubscriptionData()` returns `pendingPlanChange.plan.id`, `paymentUrl`, amount, and effective date.
- Assert payment confirmation clears pending fields when activating the selected plan.
