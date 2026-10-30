# Access-profile and permission-management delivery

Use this checklist for roles, groups, access profiles, capability matrices, and resource-scoped permissions.

## Model

- Prefer one admin-facing access concept over parallel editable Role + Group models. Existing roles can become protected system profiles; tenant-owned copies hold editable capabilities and resource scope.
- Keep global/tenant safety boundaries internal and reserved. Tenant profiles must not grant superadmin, cross-tenant, or policy-administration powers unless explicitly allowed.
- When requested, model **View** and **Edit** as separate grants. Enforce `Edit => View` in both UI behavior and backend validation.
- Require both the feature capability and applicable resource scope. Resource filtering does not replace feature authorization.

## Cross-layer enforcement

Apply the same effective capability set to:

1. navigation visibility,
2. direct-route guards,
3. API reads,
4. API mutations,
5. resource-level checks such as allowed menu categories/items.

Treat profile edits as revocations: invalidate or refresh sessions for affected users immediately.

## Completion audit

Do not accept an implementation report based only on policy tests. Inspect the real management UI and endpoints and confirm:

- create,
- duplicate protected defaults,
- edit/update,
- separate View/Edit controls,
- assignment of existing users,
- protected system-profile behavior,
- deletion/reassignment guards,
- resource selectors and effective-count feedback,
- session invalidation.

**Pitfall:** A page that only creates a profile from a base profile is scaffolding, not completed feature management.

## Release proof

Add a public E2E that duplicates or creates a profile, configures View/Edit and resource scope, assigns a user, signs in as that user, verifies visible and hidden features/resources, and submits a crafted forbidden mutation to prove server-side denial. Existing role/system-profile parity should also be regression-tested.
