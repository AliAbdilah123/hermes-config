# Subscription expiry status and in-app notification

Use when short-lived/test plans (for example `minute_1` / `minute_2`) appear to stay active after `current_period_end`, or when the user expects an immediate expired-plan banner.

## Root cause pattern

The payment activation path can correctly set `subscriptions.current_period_end` from `PlanPeriod(planID)`, but `/api/subscription/status` may still query only `WHERE status='active'` and return the plan as active forever unless the status helper compares `current_period_end` to `time.Now()`.

## Backend fix shape

- Keep `PlansData()` as the single source for test plan prices and `billingCycle: "1_MINUTE"`.
- Keep `PlanPeriod(planID)` in the activation / invoice effective-date path so `5000` and `10000` plans really get one-minute periods.
- In `models.SubscriptionData(db, userID)`:
  1. Query the active subscription.
  2. Parse `current_period_end` as RFC3339.
  3. If `periodEnd <= now`, update that row to `status='expired'` and return a status payload with `status: "expired"`, preserving the expired `plan.id`, name, price, quota, and period dates so the UI can explain what expired.
- Add tests for both paths:
  - active `minute_1` with past `current_period_end` returns/stores `expired` and still reports price `5000`.
  - active `minute_2` with future `current_period_end` stays active and reports price `10000`.

## Frontend fix shape

- Add a global authenticated-layout banner, not only Settings-page copy, so users see the expiration while using the app.
- Fetch `/api/subscription/status` and show a banner when `status === "expired"` or when a paid plan's `currentPeriodEnd` has passed locally.
- Schedule the next status check for the exact `currentPeriodEnd + small buffer` when available; otherwise poll lightly (for example 15–30s). This makes one-minute plans feel immediate without high-frequency polling.
- Keep a dismiss button scoped to the current plan id so a new plan can show a new banner.

## Verification

```bash
cd apps/backend-go
gofmt -w internal/models/models.go internal/models/subscription_test.go internal/subscription/handler.go internal/subscription/*_test.go
go test ./internal/models ./internal/subscription
go build -o /tmp/socialzen-api .

cd ../frontend
pnpm typecheck && pnpm build
```

After deploy:

```bash
curl -s http://127.0.0.1:8089/api/plans | python3 -m json.tool | grep -A3 -E 'minute_1|minute_2'
# verify minute_1 => price 5000 + billingCycle 1_MINUTE
# verify minute_2 => price 10000 + billingCycle 1_MINUTE

curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<current-index>.js" | grep -i content-type
# expected: application/javascript
```
