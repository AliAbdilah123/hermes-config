# Discovery database merchandising implementation handoff

Use this reference when an approved Komuna Discovery prototype must become an agent-ready implementation plan using real program records.

## Preserve prototype parity without duplicating the app

Treat the approved prototype as the composition and interaction source of truth, but implement it with existing application primitives:

- reuse `TopNav`, `Footer`, `ProgramCard`, `ProgramGrid`, `apiClient`, i18next, theme state, and React Router;
- keep all real auth-dependent navigation and route visibility rules;
- do not paste static prototype cards, sample prices, absolute production links, or duplicate footer/topbar markup into React;
- scope redesign CSS to Discovery so Search Programs, Program Detail, dashboard, wallet, checkout, and auth pages remain unchanged.

When the user likes a prototype topbar but asks for “available navigations,” preserve its visual treatment while restoring only routes that actually exist. Never invent a topbar destination merely because an informational anchor exists farther down the landing page.

## Mutually exclusive section selection

Build all landing sections from one consistent fetched candidate set. A small pure selector is preferred over three unrelated requests.

Recommended rules:

1. Filter to records eligible for public discovery according to approved policy.
2. **Most Popular:** sort by `memberCount DESC`, then `rating DESC`, then stable `name ASC`; take the section limit.
3. Add selected IDs to a `Set`.
4. **New Programs:** exclude used IDs, sort by `created_at DESC`, then stable `name ASC`; take the limit.
5. Add those IDs to the same `Set`.
6. **Open to Join:** retain `public` and `need_approval`, exclude all used IDs, Fisher–Yates shuffle a copy, then take the limit.
7. Never backfill with duplicates. Hide only sections with no records.

The section selector should accept an injected RNG. This makes random selection deterministic in unit tests and avoids mocking global state.

## “Random on reload” lifecycle semantics

“Changes every reload” means randomize once after a successful page-load fetch, not during rendering.

- Compute and store the selected sections when the response arrives.
- Do not place `Math.random()` in render or in a memo whose dependencies change for theme, language, membership, carousel, or unrelated state.
- A full remount/reload may produce a new Open sample.
- A deliberate retry that successfully fetches again may also produce a new sample.
- Do not use SQL `ORDER BY RANDOM()` when other sections must exclude the same records; one frontend selection pass over a consistent dataset is easier to reason about and test.

## API boundary

First inspect the existing list DTO and endpoint. If it already contains IDs/slugs, visibility, image URL, creation time, member count, rating, and card presentation fields, avoid schema work.

For a modest catalog, one paginated request with an explicit merchandising ceiling can be enough. If production can exceed that ceiling and complete-set correctness matters, add validated API sort/filter support or a dedicated Discovery endpoint. Do not introduce a migration solely for landing categorization when existing columns already express the rules.

## Carousel handoff

The hero carousel should consume real fetched `ProgramListDTO` records:

- route with `slug || id` using React Router `Link`;
- use real root-relative image URLs and the existing image fallback;
- autoplay on a fixed interval, clean up timers, pause on hover and keyboard focus;
- dots must be keyboard-operable and expose current state;
- reduced-motion preference disables autoplay, not only CSS transitions;
- one slide does not need a timer; zero usable images gets a deliberate decorative fallback.

## Navigation invariants

Before styling `TopNav`, record exact invariants from the component and tests:

- brand, Search Programs, Dashboard, sign-in, and sign-up route destinations;
- auth/workspace rule controlling Dashboard visibility;
- theme, language, notification, and profile component instances;
- guest/authenticated branches and accessible labels.

Prefer CSS/class hooks. Modify JSX only where necessary to remove obstructive inline styles or add stable hooks.

## Required tests

- Popular ordering and tie-breaks.
- New ordering and exclusion of Popular IDs.
- Open visibility policy and exclusion of both prior sections.
- No duplicate ID across any section.
- Injected shuffle determinism and no mutation of source array.
- Open sample stability across rerenders and change across remounts with different RNG sequences.
- Short datasets and empty remainder.
- Carousel timer advancement/cleanup, dot selection, pause/resume, reduced motion, image fallback, and slug-first links.
- Existing topbar routes/conditional controls.
- Exactly one shared footer/contentinfo landmark.
- Absence of rejected decorative labels such as “Curated discovery” and section numbering.

## Review artifact and gate

Update the separate prototype minimally with the final navigation/label decisions, then publish a separate comprehensive plan page. Verify both public URLs with cache-busting and HTTP 200. The plan must include exact paths, selector semantics/code, tests, responsive acceptance, regression boundaries, and an explicit implementation/deployment gate.
