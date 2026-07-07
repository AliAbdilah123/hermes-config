# Komuna admin dashboard tabs for session operations

When adding admin-only operational flows in Komuna (for example session templates and generated-session activation), prefer placing them as tabs inside `AdminDashboardPage` when the user asks for dashboard consolidation instead of creating more sidebar routes.

## Pattern

- Keep the underlying page components reusable by adding an `embedded?: boolean` prop.
  - Standalone route: render the page hero and outer padding.
  - Embedded tab: hide the hero and remove extra page padding with a scoped `.embedded` class.
- Add the tab switcher directly in `apps/web/src/pages/AdminDashboardPage.tsx` near the top of the dashboard content.
- Render embedded components in the tab body:
  - `<SessionTemplatesPage embedded />`
  - `<ActivateSessionsPage embedded />`
- Remove duplicate admin sidebar/workspace navigation links for those same flows, so the dashboard tabs are the primary admin entry point.
- Keep manager-specific routes/links when managers still need product-scoped access outside the admin dashboard.

## Verification

- Run the frontend production build: `npm run build` from `apps/web`.
- If only the frontend can be safely deployed because backend build is blocked by unrelated existing Go compile debt, deploy only the Vite `dist/` assets and explicitly report that backend restart was not attempted.
- Verify the deployed JS bundle contains the new tab labels, e.g. `Session templates` and `Activate sessions`.

## Pitfall

Do not leave newly-created standalone admin pages only in the sidebar if the requested UX is “inside the admin dashboard tabs.” The routes can remain as hidden/deep-link fallbacks, but the visible admin workflow should be tabbed in the dashboard.