# Route reuse and tenant administrator creation

## Sibling routes that reuse one component

When sibling React Router routes render the same component type with different props (for example, list and create tabs), React may preserve the component instance during direct navigation. Route-controlled visibility initialized once with `useState(prop === 'create')` becomes stale.

- Derive routed mode from the current prop, URL, or route match.
- Keep local state only for genuinely local variants such as an inline disclosure.
- If both coexist, combine them explicitly: `showCreate = routedCreate || inlineCreate`.
- Add a regression test that renders the first sibling route, rerenders or navigates to the second without unmounting, and asserts the second route's content appears. Fresh-mount-only tests miss this bug.
- For preview-first work, rebuild and republish the isolated preview, verify the deep route and new hashed asset, and confirm production still serves a different bundle.

## Tenant creation with an administrator picker

Treat administrator selection and tenant/program creation as one durable transaction rather than frontend decoration.

- Reuse the nearest accessible searchable-picker interaction, but do not import prototype-only components into production code.
- Provide a privileged, server-paginated users endpoint with stable ordering and server-side name/email search. Lazy loading must fetch later pages, not slice an already-loaded list.
- Require the selected user at frontend and API boundaries, verify the user exists, and transactionally create the tenant, active membership, and administrator role.
- Keep the creator as audit actor and record the selected administrator in audit details. Do not silently assign the creator unless selected.
- Make validation submit-driven and accessible: keep submit available, focus a linked error summary after an invalid attempt, connect errors with `aria-describedby`, set `aria-invalid`, and expose request status/errors through live regions.
- Derive a live preview directly from draft state, including image preview and selected administrator, so every field change is represented immediately.

## Focused acceptance checks

1. Navigate list → create without unmounting; form appears.
2. Edit each field; preview changes immediately.
3. Open picker by keyboard; search name/email; load another API page; select; close with Escape and restore focus.
4. Invalid submit focuses summary and links to fields.
5. API rejects missing/nonexistent administrator.
6. Successful creation assigns only the selected administrator and records the creator separately in audit data.
