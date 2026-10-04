# Application-copy targeting

Use this when a user asks to copy, clone, or reproduce an “app” from a product URL.

## Target resolution

1. Treat **app** as the interactive product, not the marketing homepage.
2. Inspect the supplied URL first. If it is a dead/redirecting path, inspect both the product root and application host (for example `app.<domain>`), plus public shared/demo routes.
3. Do not silently substitute the easiest public marketing page. If authentication obscures the app, use public shared canvases, demos, documentation, screenshots, and static app-shell assets as evidence.
4. When the user explicitly says to proceed without clarification, make the best evidence-backed app replica and state only unavoidable capability boundaries (auth, paid APIs, private data).

## Functional-copy acceptance

A convincing app copy needs more than matching chrome:

- reproduce the product’s central interaction model;
- make primary tools and controls work locally;
- use realistic seeded state so the workspace is immediately reviewable;
- label simulated provider behavior honestly;
- verify desktop and mobile interaction surfaces, not only screenshots;
- test the exact public deployment after promotion.

For canvas/workspace products, verify at minimum: add/select/edit/duplicate/delete, drag, connections following nodes, pan/zoom/fit, inspector behavior, keyboard controls, and responsive tool/inspector access.

## Visual QA loop

1. Build and render desktop and mobile.
2. Treat clipped nodes, obscured canvas content, off-screen inspectors, and compressed desktop chrome on mobile as release blockers.
3. Desktop side inspectors should reserve canvas space or trigger refitting.
4. Mobile inspectors should become contained sheets/drawers with internal scrolling; mobile tools need touch-sized controls.
5. Re-capture after corrections and only deploy after both viewport reviews pass.
