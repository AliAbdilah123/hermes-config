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

## Pitfall

If `SubscriptionData` only exposes the broad tier (`TIER_1`, `TIER_2`) and the frontend computes current-plan selection from `status.tier.toLowerCase()`, a one-minute plan that maps to the same quota tier as a monthly plan can make the wrong card look current. Return/use `status.plan.id` for card identity.