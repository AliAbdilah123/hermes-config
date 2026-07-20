# SocialZen one-minute subscription plans

Use this when adding short-lived/test subscription plans while preserving the existing Xendit subscription flow.

## Key pattern

- Add the plan(s) to `apps/backend-go/internal/models/models.go` in `PlansData()` so `/api/plans` and invoice amount lookup use the same source.
- Do not hardcode every new duration in handlers. Add/reuse a small helper like `PlanPeriod(planID)` that maps plan metadata (`billingCycle == "1_MINUTE"`) to `time.Minute`, otherwise defaults to the existing monthly period.
- Use that helper in:
  - mock subscription response `effectiveDate`
  - real Xendit invoice response `effectiveDate`
  - payment confirmation activation (`applyPaidExternalID`) when writing `current_period_end`
- Add each short-lived plan to `SubscriptionData`'s `tierMap`; return `plan.id` in the status payload so the frontend can distinguish `minute_1` from normal `tier_1` even if both map to `TIER_1` quota semantics.
- Update frontend plan ordering (`TIER_ORDER`) and analytics `PlanId` union for new plan IDs.
- If TypeScript `SubscriptionStatus.plan` previously lacked `id`, update fixtures/tests that construct paid plans.

## Minimal verification

```bash
cd apps/backend-go
gofmt -w internal/models/models.go internal/subscription/handler.go internal/subscription/*_test.go
go test ./internal/subscription ./internal/models
go build -o /tmp/socialzen-api .

cd ../frontend
pnpm typecheck && pnpm build
```

After deploy:

```bash
curl -s http://127.0.0.1:8089/api/plans | python3 -m json.tool | sed -n '1,80p'
# verify new plans expose price and billingCycle, e.g. 5000/10000 and 1_MINUTE
```

## Removing short-lived plans safely

Treat **purchase availability** and **legacy subscription interpretation** as separate concerns:

- Remove retired plan IDs from `PlansData()`. The plans endpoint and invoice creation both iterate this list, so this removes the cards and prevents new invoices/selections.
- Keep legacy entries in `planInfo()` and preserve their duration in `PlanPeriod()`. Existing active, pending, paid, or recently expired subscriptions may still contain those IDs and must retain their original name, price, quota, and expiry semantics.
- Do not delete historical subscription rows as part of plan retirement.
- Add a focused test proving retired IDs are absent from `PlansData()`, then run existing subscription/model tests to prove legacy rows still deserialize and expire correctly.

## Pitfalls

- If `SubscriptionData` only exposes the broad tier (`TIER_1`, `TIER_2`) and the frontend computes current-plan selection from `status.tier.toLowerCase()`, a one-minute plan that maps to the same quota tier as a monthly plan can make the wrong card look current. Return/use `status.plan.id` for card identity.
- Removing retired IDs from `planInfo()` or their special case in `PlanPeriod()` silently reinterprets legacy subscriptions as the default monthly Starter plan. Retire them from `PlansData()` only.