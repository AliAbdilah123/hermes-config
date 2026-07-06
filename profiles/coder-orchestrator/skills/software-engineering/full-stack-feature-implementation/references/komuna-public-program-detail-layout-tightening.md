# Komuna public ProgramDetailPage layout tightening

Use when the public Komuna program detail page feels messy, too tall, or wasteful after selecting a program from discovery.

## Pattern

1. Verify the target is the **public** route (`/programs/:id`), not dashboard/admin program detail routes.
2. Use Playwright with mocked or live program/session data to measure:
   - hero top/bottom/height;
   - session column top;
   - mobile body/hero/stats heights;
   - horizontal overflow.
3. Main spacing culprits found in the live implementation:
   - forced viewport hero height such as `minHeight: calc(100vh - nav - extra)`;
   - `justifyContent: space-between` spreading hero text, CTA, and stats apart;
   - a separate guest banner above breadcrumbs/hero pushing real content down;
   - guest users seeing competing CTAs (`Sign in`, `Join program`, `Reserve`) instead of one coherent auth action;
   - decorative placeholder imagery dominating over useful session content.
4. Tighten with the smallest seams:
   - remove the page-level guest banner and put auth intent in the primary CTA;
   - pass `isAuthenticated` into the hero CTA and label guest CTA `Sign in to join`;
   - pass optional `bookLabel` through `HeroRightSessions` → `SessionCardCompact` so guest session buttons say `Sign in` while authenticated users still see `Reserve`;
   - remove forced hero `minHeight` and replace `space-between` with `flex-start`;
   - reduce grid gaps and align both columns to `start`;
   - keep sessions visible high in the page;
   - remove stray decorative glyphs (e.g. `§`) from section headings unless explicitly part of the approved design.
5. Verify with both focused tests and browser-level layout checks:
   - focused tests for ProgramDetailPage and compact session card copy;
   - production Vite build with `env -u VITE_NEON_AUTH_URL npm run build`;
   - Playwright local/live checks for `Sign in to join`, `UPCOMING SESSIONS`, no stray glyph, and no horizontal overflow.

## Notes

- Existing tests may mock auth as guest globally. If guest CTA copy changes from `Join program` to `Sign in to join`, update tests to assert the product behavior rather than preserving old copy.
- For deployed Komuna frontend rebuilds, still verify the deployed JS bundle contains the new CTA marker and does not contain stale Neon Auth markers.
