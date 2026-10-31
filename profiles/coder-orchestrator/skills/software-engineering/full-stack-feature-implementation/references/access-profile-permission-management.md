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

## Terminology and management-surface migrations

When product language changes (for example, Access Profiles → Roles), first separate user-facing terminology from persistence contracts:

- Rename headings, tabs, field labels, buttons, help text, navigation, docs, and accessible names consistently.
- Preserve API paths, database tables, capability keys, and stable IDs unless the user explicitly requests a breaking migration. A UI-only rename is usually the smallest safe release.
- Search touched UI tests for both the required new term and absence of the obsolete term.
- Keep protected/system records visibly distinct from editable tenant-owned records.

For admin collections, prefer semantic tables with native client-side search/filter/stable sorting while the API already returns bounded datasets. Add server pagination only when measured size requires it. Use sortable header buttons with `aria-sort`, responsive overflow, explicit result counts, and relevant filters rather than introducing a table dependency.

Use the product's existing accessible modal for create/edit forms instead of appending forms below lists. Verify dialog name, initial focus, Escape, focus return, cancel/save actions, and narrow-screen scrolling. Quick enable/disable row actions may remain outside the modal, but destructive disable should require confirmation.

Global-superadmin modules need an explicit global-role/scope guard in navigation and routing; a generic tenant-admin capability is not sufficient. Keep backend authorization as the final boundary and test both hidden navigation and direct-route denial.

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
- search/filter/sort behavior and empty results,
- modal keyboard/focus behavior,
- global-versus-tenant route visibility where applicable,
- session invalidation.

**Pitfall:** A page that only creates a profile from a base profile is scaffolding, not completed feature management. Likewise, changing visible terminology does not justify renaming stable persistence contracts in the same release.

## Release proof

Add a public E2E that duplicates or creates a profile, configures View/Edit and resource scope, assigns a user, signs in as that user, verifies visible and hidden features/resources, and submits a crafted forbidden mutation to prove server-side denial. Existing role/system-profile parity should also be regression-tested.
