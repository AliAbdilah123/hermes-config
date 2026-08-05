# Session-detail Simple product package picker

Use this pattern when a session-detail disclosure lets an attendant select a Simple product or buy a package because no eligible voucher-backed choice exists.

## UI contract

- Render eligible Simple product choices as a vertical radio list.
- Reuse the established booking/checkout package-choice component for purchase recommendations; do not invent a second card design.
- Recommend only active packages containing a `simple` product entry whose benefit type is `voucher`; exclude session products and subscription-only Simple product entries.
- Preserve API order and cap recommendations at three.
- Lay the package choices out horizontally. At narrow widths, keep each card usable and allow horizontal scrolling with scroll snap rather than squeezing cards.
- If one or two eligible packages exist, render only those. Do not pad the row.
- If none exist, keep the surface visible and show an explicit empty state rather than hiding the section.
- Keep selection and checkout behavior owned by the existing checkout-choice component.

## Focused verification matrix

Cover these states independently:

1. An eligible Simple product voucher exists: vertical product selection renders and package fallback does not replace it.
2. No eligible voucher and zero eligible packages: exact empty-state copy renders; checkout action is absent.
3. One and two eligible packages: correct radio count, first package defaults selected, another package can be selected.
4. More than three eligible packages: only the first three API-ordered eligible packages render.
5. Mixed entries: archived, session-only, and subscription-only packages are absent.
6. Desktop and narrow viewport: row remains horizontal; narrow viewport scrolls rather than collapsing into an unreadable grid.

Build with the exact preview base, publish to the existing isolated preview route, and verify the lazy route chunk/public rendered state. If the changed controls require authentication and the browser only proves the signed-out shell, report authenticated visual E2E as pending rather than calling the UI ready.
