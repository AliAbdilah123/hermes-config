# Template-to-tenant role delivery and public E2E

Use this pattern when global role templates are copied into tenant-owned roles.

## Data and authorization invariants

- Store templates separately from tenant roles.
- On tenant creation, copy every template into new tenant-owned records with distinct IDs.
- Migrate existing `system:*` assignments to the matching tenant-owned role.
- Scope tenant role edits by both role ID and tenant ID.
- Require global superadmin authorization on template endpoints, not only a hidden UI tab.
- Template updates affect future copies only; never silently rewrite existing tenant roles.
- Editing one tenant's role must not mutate another tenant or its source template.

## Tests that must fail before implementation

Backend tests prove copied IDs differ across tenants, tenant admins can edit copied built-ins, cross-tenant writes fail, template endpoints reject tenant admins, superadmins can edit templates, new tenants receive updated templates, and legacy global assignments are remapped.

Frontend tests separately prove tenant rows expose Edit, superadmins see Template Roles, template saves use the template endpoint without tenant business data and reload templates, and tenant saves keep using the tenant-role endpoint.

## Public release verification

Do not infer UI readiness from API tests or DOM data: responsive CSS can hide an action column that exists in the DOM.

After deployment verify:

- mobile tenant admin: open Roles, wait for actions, assert Edit is visible, open it, and assert no page overflow;
- desktop superadmin: edit a harmless template field, verify persistence, then restore it;
- browser `pageerror` collection stays empty;
- local and public health checks pass after an explicit service-readiness loop.

Wait for the first asynchronously rendered action before asserting counts. Inspect accessible names before choosing locators: `aria-label="Edit Admin"` does not match an exact accessible-name query for `Edit`, despite visible text saying Edit.

## Orchestration pitfall

A subagent's passing summary is not release evidence. Re-read modified files, rerun canonical checks in the parent workspace, deploy the real artifact, and execute public E2E. If public E2E exposes an integration defect, add a failing regression first, patch minimally, redeploy, and repeat before reporting READY.
