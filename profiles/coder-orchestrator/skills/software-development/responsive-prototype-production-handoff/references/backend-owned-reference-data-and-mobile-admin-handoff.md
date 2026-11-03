# Backend-owned reference data and mobile admin handoff

Use this when a responsive admin cleanup also removes frontend-only sample/reference data.

## Runtime data ownership

1. Search every runtime import of fixture modules, not only the reported screen. Tenant/business labels commonly leak into shell selectors, payment screens, image alt text, and dashboards.
2. Keep fixtures in tests, seed/reset code, and explicit development tooling; remove them from production component/store initialization.
3. If all authenticated roles need reference labels, expose one scoped backend read:
   - global admins receive all authorized records;
   - tenant users receive only records named in their assignments;
   - mutations remain privileged separately.
4. Bootstrap reference data with session/state data. Do not render frontend fallback labels that can silently disagree with the database.
5. Update test fetch mocks with the exact endpoint response shape before changing store bootstrap.

## Compact admin mobile pattern

- Use the shared field primitive for every label/control pair; do not mix stacked fields with ad-hoc inline `<label><select>` markup.
- Put checkbox and text in one flex row with `align-items:center` and an explicit minimum touch height.
- Align action buttons and result counts through the parent layout. Handle singular/plural result copy at the data-table boundary.
- Remove mobile table `min-width` only when the remaining visible columns fit; hide low-priority columns deliberately and keep primary identity/action columns visible.
- Verify rendered geometry, not CSS declarations: page `scrollWidth <= clientWidth`, full-width field bounds, and checkbox/text center delta near zero.

## Release verification

1. Run focused RED/GREEN UI coverage, backend authorization tests, full frontend/backend suites, typecheck, lint, and production build.
2. Build and deploy the committed artifact, restart the backend when its contract changed, and probe local plus canonical public app/API URLs.
3. Run a route-focused mobile browser check at the reported viewport. Assert removed sample controls/text are absent, CRUD entry points are visible, dialogs open, and console/page errors are empty.
4. Do not let a broad public E2E fixture hard-code seeded tenant labels. Resolve expected labels from the API or scope the E2E to invariant behavior; operational database names may legitimately differ from seed fixtures.
5. If the broad suite fails on stale fixture copy but the feature route is healthy, fix that suite before calling the whole suite green; meanwhile report the focused route evidence precisely.
