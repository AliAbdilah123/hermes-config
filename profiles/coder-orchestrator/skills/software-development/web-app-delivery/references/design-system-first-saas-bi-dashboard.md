# Design-System-First SaaS / BI Dashboard Delivery

Use this reference when the user supplies a visual design reference and asks to build a SaaS, CRM, BI, marketplace, or admin-style web app.

## Session learning

For product builds like Local Business OS Indonesia, the user may explicitly require: **build the design system first, then the app**. Treat this as a delivery sequence requirement, not just a design note.

## Recommended sequence

1. **Extract visual system from the reference image before implementation.** Capture:
   - Color palette and contrast behavior.
   - Typography scale and heading/body rhythm.
   - Card shapes, radius, borders, shadows, and glass/gradient treatment.
   - Navigation layout, dashboard density, table/list styling, charts, filters, and CTAs.
   - Empty/loading/error states and mobile behavior.
2. **Create a small component-level design system first.** At minimum:
   - CSS variables/design tokens.
   - App shell/sidebar/topbar.
   - Cards/stat tiles.
   - Buttons/input/select/search/filter chips.
   - Tables/lists/business profile cards.
   - Badges/status pills/progress bars/opportunity score visuals.
   - Modal/drawer/form patterns.
3. **Use those components for all product screens.** Do not hand-style each screen independently.
4. **Build a realistic seeded-data MVP.** For intelligence platforms, show believable workflows even before real crawlers/connectors exist:
   - Business discovery/search/filtering.
   - Business detail and monthly snapshot model.
   - Opportunity scoring/reasons/service recommendations.
   - CRM/lead pipeline.
   - Market intelligence reports/heatmaps/leaderboards.
   - Website/audit/content generation placeholders backed by deterministic demo data or API stubs.
5. **Verify both function and visual delivery.** Run builds/tests, curl API routes, and do at least one visual/browser smoke check for the actual deployed UI when design fidelity matters.

## Implementation notes

- Keep the user's approved stack stable. If the source spec recommends a different hosted stack but the local deployment standard is React/Vite + Go + SQLite + nginx, revise the PRD/contract first and then build that stack.
- For Indonesia/local-business products, default UI copy can be Bahasa Indonesia-first with English technical labels, and seed data should use Indonesian city/category examples.
- If external scanning APIs are not ready, implement importer/connector abstractions plus seeded/imported datasets rather than pretending live scanning exists.
- Generated customer websites can be server-hosted static previews first; leave external provider deployment as a later connector unless explicitly requested.
