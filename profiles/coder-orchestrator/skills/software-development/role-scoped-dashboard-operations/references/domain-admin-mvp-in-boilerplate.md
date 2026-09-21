# Domain Admin MVP in an Existing Boilerplate

Use when adding a product-specific admin view to an app that still contains generic SaaS/admin infrastructure.

## Inspection checklist

1. Identify the actually mounted frontend entry point. Existing route registries or admin shells may be orphaned and are not evidence users can reach them.
2. Trace current authentication/session and tenant-admin authorization before designing access control.
3. Distinguish generic billing tables from the requested domain ledger. Do not overload a generic payment model when it lacks domain identity, billing period, payer, or lifecycle fields.
4. Inspect migration semantics. If applied migrations are checksum-tracked, add a migration; never edit an applied one.
5. Probe public API paths for expected content type/body, not only HTTP 200. SPA fallback can make an undeployed API look healthy.

## Minimal architecture

Prefer extending the mounted product shell over reviving an orphaned generic runtime. Add only domain tables and read APIs needed by the view. Derive aggregate totals in SQL rather than storing duplicate balances. Use integer currency units and canonical periods/dates.

A useful inspection-oriented admin split is:

- Asset/property registry with constrained kind and occupancy/use status.
- Periodic charge ledger uniquely keyed by asset and billing period.
- Cashflow entries plus API-side aggregation; include paid periodic charges as income without duplicating stored totals.

Seed deterministic, idempotent demo records only when authenticated public E2E needs persisted data.

## Ordered delivery

1. Schema, constraints, and idempotent seeds; test invalid enums and duplicate prevention.
2. Protected read APIs; test admin/super-admin success and member, unauthenticated, and cross-tenant denial.
3. First admin slice in the existing UI; preserve resident/member behavior.
4. Add remaining ledger/dashboard slices one at a time, rerunning focused tests after each.
5. Run full backend tests, frontend tests, and production build.
6. Deploy the API and configure its reverse-proxy location before SPA fallback.
7. Public authenticated E2E: log in, open admin view, compare representative UI rows/totals with API responses, test mobile, and inspect console/network errors.

Stop at the first failing milestone; do not continue and defer it.

## Deployment pitfall

A public `200` at `/api/...` is insufficient evidence that an API exists. Verify JSON content and content type, then authenticate and call a protected endpoint.

## Scope ceiling

For a read-only MVP, omit CRUD, imports, chart libraries, new routers, repository abstractions, and revived generic admin frameworks. Add them only when editing, bulk ingestion, visualization complexity, or demonstrated reuse requires them.
