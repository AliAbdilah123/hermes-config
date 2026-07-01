# React SPA page-split refactor with TDD

Use when splitting a section out of one page into a new dedicated route — a common UX refactor where an overcrowded page is simplified and a section is moved to its own page.

## Pattern: "Showcase + Utility Split"

When a single page tries to serve two audiences (browsing/inspiration vs. active search/filtering), split into:

- **Original page (showcase):** remove search/filter controls, show a small curated subset (e.g. first 6 items), add a CTA link to the new page.
- **New page (utility):** move the full search/filter/results section verbatim, preserving all markup, styles, and responsive behavior.

## TDD approach for page moves

The key insight: tests must assert BOTH that the old page lost controls AND the new page gained them.

1. Write failing tests for the new page (component doesn't exist yet → RED).
2. Write failing tests for the old page asserting controls are gone (old page still has them → RED).
3. Create the new page by copying the old page's component and renaming the export.
4. Simplify the old page: remove search/filter imports and state, fetch a small limit, render a showcase grid, add CTA link.
5. Run both test suites → GREEN.

## Test-writing specifics

- When the old page has duplicate CTA links (hero + section), use `getAllByRole` not `getByRole` to avoid "found multiple elements" errors.
- When category filter buttons share a name prefix with quick-filter buttons (e.g. "Boxing near me" vs "Boxing"), use exact-match regex: `/^Boxing$/i`.
- Assert the API call shape changed: `expect(getPaginated).toHaveBeenCalledWith('/programs', { page: 1, limit: 6 })` for the showcase page.

## Copy-not-refactor rule for section moves

When the user says "preserve the style and structure" of the moved section:
- Copy the source page file verbatim, rename the export function, and change nothing else.
- Do NOT refactor shared logic into hooks or extract components during the move.
- CSS classes (e.g. `.discovery-programs`, `.discovery-layout`, `.category-sidebar`) apply globally and work on the new page without any CSS changes.
- Only remove unused imports from the SIMPLIFIED page, not from the moved/copied page.

## Route ordering pitfall

In React Router, a static route (`/programs`) must be declared BEFORE its dynamic sibling (`/programs/:id`) to avoid the param route swallowing the static path. Place the new route above the dynamic one in `App.tsx`.

## Pre-existing build errors

When building a Vite SPA with uncommitted changes from other work, `tsc -b` may fail on unrelated files. Fix minimally:
- `currentList.map(...)` → `currentList!.map(...)` when TypeScript can't narrow a ternary that set the variable to `null` in one branch but you're in the `else` branch.
- Enum value mismatches (e.g. `'used'` → `'claimed'` when the DTO type was updated but the component wasn't) — fix all occurrences with `replace_all`.
- Do NOT fix broad lint debt during a page-split task; report unrelated lint failures separately.
