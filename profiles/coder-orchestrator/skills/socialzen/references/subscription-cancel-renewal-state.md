# Subscription cancel renewal state

When cancellation should keep paid access until period end but stop renewal:

- Persist an explicit `subscriptions.cancel_at_period_end INTEGER NOT NULL DEFAULT 0` flag. Do not rely on frontend local state or change `status` away from `active` before `current_period_end`.
- `/api/subscription/cancel` should be idempotent-ish for active subscriptions: set `cancel_at_period_end=1`, clear pending invoice fields, and return `SubscriptionData()` so reloads show the server truth.
- `SubscriptionData()` should return `status: "active"` plus `cancelAtPeriodEnd: true` while the plan is still within period. If the period has passed and `cancelAtPeriodEnd` is true, return free-tier data rather than an expired paid plan.
- Pending/continuation invoices must be suppressed when `cancel_at_period_end=1`. If pending invoice fields exist from before cancellation, do not surface `pendingPlanChange`.
- Continuation invoices should only be auto-created shortly before expiry (currently within 24h), only for active paid subscriptions that have not canceled and do not already have a pending invoice.
- UI status shape:
  - active + not canceled: green `active`, cancel button visible.
  - active + canceled: yellow `Active · won’t renew`, cancel button removed, no popup invoice.
  - canceled and period ended: Free tier.

Verification checklist:

```bash
cd /home/ubuntu/socialzen/apps/backend-go
gofmt -w internal/models/models.go internal/models/subscription_test.go internal/subscription/handler.go internal/webhook/handler.go
go test ./internal/models ./internal/subscription ./internal/webhook
go build -o /tmp/socialzen-api .

cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck && pnpm build

sudo sqlite3 /opt/socialzen/data/socialzen.db "ALTER TABLE subscriptions ADD COLUMN cancel_at_period_end INTEGER NOT NULL DEFAULT 0" 2>/tmp/socialzen_migrate_err || grep -qi 'duplicate column' /tmp/socialzen_migrate_err
sqlite3 /opt/socialzen/data/socialzen.db "PRAGMA table_info(subscriptions);" | grep cancel_at_period_end
```

Remember to reset `cancel_at_period_end=0` whenever a successful payment/webhook applies a paid plan again.