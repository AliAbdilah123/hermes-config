# Dynamic tenant registries and state envelopes

Use when a newly created tenant appears in an administrative list or selector but tenant-scoped APIs return authorization errors or missing state.

## Failure shape

A system may have two competing tenant registries:

- a durable `tenants` table used by CRUD and selectors;
- a static in-process ID set or seeded JSON envelope used by authorization and operational state.

Creating the database row updates the first registry only. The tenant is visible but unusable. Restart behavior may differ if startup hydrates only part of the runtime registry.

## Repair recipe

1. Identify every tenant source used by CRUD, authorization, session validation, aggregate reads, and state writes.
2. Make the durable tenant table authoritative for active IDs. Hydrate runtime caches from it on startup and update them transactionally on create/enable/disable.
3. Ensure every active tenant has a state-envelope entry before serving tenant-scoped reads. Initialize a minimal valid empty state; do not clone another tenant's business data.
4. Include dynamic active tenants in aggregate reads and state validation, while retaining static IDs only for seed-account generation when appropriate.
5. Keep disabled tenants in durable storage and existing state, but remove them from authorization. Re-enabling must restore access without losing prior state.
6. Persist initialized state during startup or tenant creation; do not rely on a response-only migrated object that disappears on restart.

## Regression matrix

- Create tenant -> immediate scoped state read succeeds.
- Create tenant -> users and roles endpoints accept its ID.
- Restart -> created tenant remains authorized and initialized.
- Disable -> scoped access fails.
- Re-enable -> scoped access succeeds and prior state remains.
- Global aggregate read includes active dynamic tenants and excludes disabled tenants according to product policy.
- Existing seeded tenants and tenant isolation tests remain green.

## Verification

Inspect the database used by the running service, not an assumed repository database. Compare active rows in `tenants` with keys in the persisted state envelope; the missing-key set must be empty. Then restart the service and run authenticated public E2E against both a seeded tenant and a dynamically created tenant.
