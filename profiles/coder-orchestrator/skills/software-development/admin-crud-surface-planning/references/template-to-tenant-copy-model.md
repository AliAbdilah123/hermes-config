# Template-to-tenant copy model

Use this checklist when global defaults seed independently editable tenant records.

## Data model

- Global template table: stable template ID, name, capabilities/settings, active/version metadata.
- Tenant record table: unique tenant-owned ID, tenant ID, copied values, optional `source_template_id` provenance.
- User/resource assignment references the tenant-owned ID, never the global template ID.
- Uniqueness prevents duplicate copies for one tenant/template pair while still allowing tenant-created records without provenance.

## Creation and migration

1. Start one transaction.
2. Create the tenant.
3. Read active templates.
4. Insert independent tenant copies with fresh IDs and provenance.
5. Assign initial tenant users to copied IDs.
6. Commit; roll back the tenant if copying fails.

For existing tenants, make the backfill idempotent: insert missing copies, map legacy global/system assignments to the matching tenant copies, verify no assignments remain on global IDs, then retire the compatibility path.

## API and UI boundaries

- Tenant list/read/write endpoints always filter by tenant ID and verify actor access server-side.
- Template endpoints require explicit global-superadmin scope for reads and writes.
- Tenant Roles tab shows Edit for all tenant-owned records when the actor has edit permission; names such as Admin or Cashier do not imply protection.
- Template Roles tab appears only for global superadmins and clearly says updates seed future tenants rather than overwrite existing ones.
- If propagation to existing tenants is ever needed, design it as a separate previewable operation with conflict policy and audit—not an incidental template save.

## Required tests

- New tenant receives one independent copy of each active template.
- Copies and templates start with equal values but distinct IDs.
- Editing tenant A changes neither tenant B nor the template.
- Editing the template changes a subsequently created tenant but not existing tenants.
- Tenant admin can edit copied roles in its tenant and cannot access another tenant's IDs.
- Non-global admins cannot read or mutate templates by direct API calls.
- Migration preserves user assignments and remains safe when run twice.
- Reload proves persistence; public E2E proves the tenant Edit action and superadmin-only Template Roles tab.
