---
name: admin-crud-surface-planning
description: Plan administrative CRUD surfaces for tenants, users, roles, permissions, and other managed records in an existing product without unnecessary contract or schema churn.
version: 1.0.0
metadata:
  hermes:
    tags: [planning, admin, crud, authorization, tables, modals]
---

# Admin CRUD Surface Planning

Use when planning management pages for tenants, users, roles, permissions, or similar administrative records in an existing product.

## Inspection order

1. Inspect the current route, navigation, page, shared form/dialog components, API handlers, schema, authorization checks, and existing tests.
2. Verify whether the requested backend lifecycle already exists before proposing endpoints or migrations. A missing page does not imply a missing API.
3. Separate product-language changes from persistence changes. If the current contract is sound, prefer changing visible labels while retaining endpoint names, columns, IDs, and capability keys.
4. Identify the exact privileged scope. Distinguish global superadmin access from ordinary tenant-admin capabilities; a generic admin route guard is not sufficient for global operations.
5. Reuse the product's existing modal and table patterns. Do not add a table/form package for client-sized datasets when native state, semantic tables, and existing components suffice.

## Required plan details

For each management surface, specify:

- searchable fields;
- filter dimensions and values;
- sortable columns and ascending/descending behavior;
- semantic columns and row actions;
- create/edit form location and lifecycle;
- enable/disable versus delete semantics;
- loading, error, empty, and no-results states;
- responsive table behavior;
- keyboard/focus behavior for dialogs;
- authorization boundary and server-side enforcement;
- persistence/reload acceptance checks.

## Terminology-only migrations

When renaming a concept such as “Access Profiles” to “Roles”:

- enumerate all touched user-facing labels, headings, buttons, help text, empty states, and validation messages;
- explicitly list internal identifiers that remain unchanged for compatibility;
- add a UI assertion that obsolete terminology is absent;
- do not rename database tables or API paths merely for cosmetic consistency;
- postpone contract migration unless the old name causes a real domain mismatch outside presentation.

## Reversible status operations

Prefer reversible enable/disable over deletion when records anchor tenant or access history. Keep disabled records visible to authorized administrators while denying normal operational access. Specify whether disabling needs confirmation, what happens if the record is currently selected, and how the list refreshes after mutation.

## Review artifacts

When UI approval is required, publish separate plan and design pages. The design page must mirror the current application shell and tokens, show representative enabled/disabled and system/custom states, and demonstrate modal placement plus table controls. Label it clearly as a static design preview, not the live application.

## Minimal verification ladder

1. Focused frontend tests fail before implementation.
2. Route/navigation visibility tests cover privileged and non-privileged roles.
3. Backend tests cover authorization and lifecycle persistence.
4. Typecheck, lint, full frontend/backend tests, and build pass.
5. Rebuild/restart/deploy the real artifact.
6. Public E2E verifies search/filter/sort, modal keyboard behavior, lifecycle persistence, authorization, and browser console health.
7. Update the project changelog before commit/push.

## Pitfalls

- Do not infer missing backend support from missing frontend navigation.
- Do not let a UI rename trigger an unnecessary schema migration.
- Do not expose global operations through a shared tenant-admin capability without an explicit global-scope check.
- Do not call cards or status rows a “proper table”; specify semantic headers and concrete controls.
- Do not treat HTTP 200 alone as visual verification. If browser rendering cannot be inspected, report that limitation without blocking publication verification.

## Supporting reference

See `references/admin-management-checklist.md` for the compact inspection and acceptance checklist.
