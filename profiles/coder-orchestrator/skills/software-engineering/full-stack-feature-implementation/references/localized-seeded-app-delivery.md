# Localized seeded-app delivery

Use when localizing an already-deployed application whose user-facing copy comes from both frontend literals and persisted seed data.

## Delivery sequence

1. Inventory user-facing text in the frontend, API errors, seed fixtures, and database-backed package/material records. Translating only JSX leaves authenticated content in the old language.
2. Keep identifiers and protocol values stable (`admin`, `learner`, route names, API fields). Translate labels, not internal symbols; broad string replacement can accidentally rename TypeScript types, component names, or props.
3. Update seed statements for fresh installs **and** migrate existing deployed rows explicitly. Seed-on-empty logic does not update a live database.
4. Update interaction tests to assert localized accessible names and representative persisted content.
5. Run tests and production build after replacement; TypeScript compilation is a useful guard against accidental identifier translation.
6. Deploy frontend and backend, apply the live data migration transactionally, restart, then wait for readiness instead of treating an immediate post-restart connection refusal as failure.
7. Public E2E must cover unauthenticated and authenticated states at desktop and mobile widths. Use the navigation control actually visible at each breakpoint (for example, mobile tabs rather than an off-canvas desktop/sidebar button).
8. Capture screenshots of the redesigned entry surface and verify representative localized learning material after login.

## Pitfalls

- Do not translate code identifiers through global prose replacement.
- Do not assume changing seed SQL changes existing data.
- Do not reuse desktop selectors on mobile when responsive navigation renders duplicate or off-screen controls.
- Do not report localization complete from the login page alone; verify package titles and lesson material returned by the live API.
