# Product-scoped manager role UI triage

Use when an admin/member-management UI edits manager assignments for products or sessions and users report confusing save failures, role changes after reload, or irrelevant products appearing in the manager picker.

## Symptoms

- A manager-assignment modal lists non-session/simple products (for example merchandise or mats) as things a manager can lead.
- Revoking a manager from their final managed product is blocked by the API but the UI shows no visible error, leaving the modal looking broken.
- The UI silently re-adds protected/locked product IDs before save, so the submitted state can differ from the admin's visible intent.
- After reload, the durable DB state shows role/product access changed or not changed differently from the optimistic UI state.

## Investigation recipe

1. Inspect the product list feeding the modal. Verify it filters both `status == active` and the product kind/type that is actually manageable (usually session products only).
2. Trace the selected product ID set from checkbox state to API calls. Watch for code that unions selected IDs with locked IDs before computing `toAdd`/`toRemove`; that hides the admin's intent.
3. Inspect backend role delete guards for rules like `last_product_manager`. They are correct domain constraints, but the UI must surface them explicitly.
4. Query durable role tables separately from the visible row state: member roles and product-manager junction rows can diverge from optimistic frontend state.
5. Add regression tests at the UI boundary:
   - simple/non-session products are absent from the manager picker;
   - last-manager products are visibly locked/explained and no DELETE is sent;
   - API errors remain visible inside the modal and keep the dialog open.

## Minimal fix shape

- Filter the modal's product source to active session/manageable products only.
- Leave last-manager products checked and disabled; show helper text telling the admin to assign another manager first.
- Do not silently rewrite the admin's selected set on save. If a protected delete is attempted, show a specific error and return before API calls.
- Catch backend errors such as `last_product_manager`, render a human-readable modal error, and keep the modal open.
