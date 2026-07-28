# Snapshot-backed platform-management previews

Use when a review-stage SPA feature adds backend endpoints or real mutations such as tenant creation and role assignment.

## Preview isolation

- Build frontend and backend from the clean candidate commit.
- Create the preview SQLite database with `.backup` or `VACUUM INTO`; never raw-copy a live DB plus WAL.
- Run the candidate API on an unused loopback port with explicit DB and address environment values targeting the snapshot.
- Give review-lived preview APIs a supervised process/service rather than an ephemeral shell process; verify it remains active.
- Proxy a preview-scoped API prefix (for example `/previews/<slug>/api/v1/`) to the candidate API and inject that exact prefix as the SPA API base. Do not let a real review form mutate production.
- Verify preview basename, API base, deep routes, candidate asset hash, expected auth response, authenticated DTO shape, and production asset/API separation.
- Keep binaries and snapshots untracked; remove the preview process, route, DB, and assets after rejection or successful promotion.

## Reused sibling-route component pitfall

React Router may reuse one component instance when sibling routes render the same component with different mode props. Do not initialize route-controlled visibility once with `useState(prop === ...)`; derive routed mode directly from the current prop/location and reserve state for local toggles. Add a regression that navigates or rerenders from sibling A directly to sibling B and asserts B's UI appears.

## Platform-wide create flows

When a platform administrator creates a tenant/program and selects its administrator:

- Provide a super-admin-only, server-paginated users endpoint with stable ordering and server-side name/email search.
- Make the selected administrator ID required at the API boundary and verify the user exists.
- In one transaction, create the tenant, active membership, scoped admin role, and audit event. Keep the initiating platform administrator as audit actor; do not silently grant them tenant admin unless selected.
- The picker should be an accessible modal with one name/email search field, lazy loading, focus management, selection state, and retry/empty states.
- Pair the create form with a live preview derived from form state. Validation should use a focusable error summary plus field-linked help/errors and `aria-invalid`; do not disable submission solely because untouched required fields are empty, because that hides validation guidance.
- For the tenant list, prefer one search plus useful rows/cards (identity, visibility, timezone, counts/admin, preview/manage actions) over speculative filter systems.
