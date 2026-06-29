# Responsive + Data-Driven Dashboard Audit for Local Go + Vite Apps

Use when a user reports many unresponsive sections and hardcoded homepage/dashboard data in a Vite/React app backed by a local Go API.

## Pattern

1. **Audit repeated layout primitives, not just named broken pages**
   - Search the main React/CSS files for two-column grids (`page-grid`, `side-panel`, `wide-panel`), chip/tag containers, tables, modals, action rows, and cards.
   - If examples include side panels (Potential Tags, Placeholder, Output, Members), patch the shared layout classes so all current/future pages benefit.
   - Add `min-width:0`, `max-width:100%`, `overflow-wrap:anywhere`, and mobile `grid-template-columns:1fr` rules to shared page/panel classes.
   - For buttons/action rows, switch to wrapping flex or one-column grid on narrow screens.
   - For long generated values (invite links, emails, tags, snippets), allow wrapping; do not leave `white-space:nowrap` unless paired with safe horizontal scrolling.

2. **Replace hardcoded dashboard/homepage placeholders with live workspace data**
   - Move static UI rows such as fake inbox items, fixed challenge progress, fixed greetings, fixed deltas, or fixed market values to derived data from API/business/leads/account state.
   - Add/extend a backend summary endpoint when the frontend needs aggregate facts: tracked businesses, average tag count, with/without website counts, enriched contact counts, CRM pipeline counts, top city, market value, and challenge progress.
   - Keep demo/fallback data only for empty or unauthenticated states; once authenticated, prefer API values and derived client-side fallbacks.

3. **Verify through production artifacts**
   - Run project build/tests first (`npm run build`, backend tests/build).
   - Deploy static assets and backend binary/service as appropriate.
   - Verify public `index.html` points at the new hashed JS/CSS.
   - For Vite SPAs, grep deployed JS for user-facing marker copy and deployed CSS for the new responsive rule. Do not expect marker text in `index.html`.
   - Login with a safe test/admin account when available and curl protected summary endpoints to confirm aggregates are dynamic (for example challenge labels and non-zero average potential tag values).

## CSS checklist

- `.page-grid { grid-template-columns: minmax(0,1fr) <side width>; }`
- `@media(max-width:1000px){ .page-grid{grid-template-columns:1fr!important} }`
- `.panel,.wide-panel,.side-panel { min-width:0; max-width:100%; }`
- `.rules, .muted-box, .member-row, .invite-row { overflow-wrap:anywhere; }`
- `.potential-tags { min-width:0; max-width:100%; flex-wrap:wrap; }`
- Mobile action rows use `display:grid; grid-template-columns:1fr` or wrapping flex.

## Pitfalls

- Fixing only the reported component usually leaves the next side panel broken. Patch shared layout primitives.
- A dashboard can look less hardcoded while still using static fallbacks. Trace each visible number/row back to account/API/business/lead state.
- SQLite aggregate expressions can return NULL when no matching rows exist; use `COALESCE(SUM(...),0)` before scanning into Go ints.
- Average tag counts stored as JSON strings may be inaccurate if computed only with string comma counting when rows contain empty tags. If the DB aggregate returns 0 but businesses exist, compute a fallback using parsed business tags.
