# Responsive table action regressions

Use this pattern when a public E2E failure reports that row actions disappear at mobile widths.

## Root-cause check

1. Inspect the rendered column order and the responsive CSS together.
2. Treat positional selectors such as `th:nth-child(n), td:nth-child(n)` as coupled to the column schema. A newly inserted column can silently make the selector hide Actions.
3. Prefer a semantic column class or explicit hide-on-mobile metadata when the shared table supports it. For a minimal existing table, remove only the selector that hides Actions; do not redesign the table.
4. Give repeated row buttons entity-specific accessible names, for example `aria-label="Edit ${row.name}"`. This makes E2E selectors unambiguous and improves accessibility.

## Strict TDD boundary

Before production edits, add focused tests that fail for both layers involved:

- Render the real page and assert the entity-specific action is available by accessible role/name.
- Assert the mobile stylesheet no longer hides the action column, or use a real viewport/browser assertion when the repository already has a browser harness.

A DOM-only test cannot prove CSS visibility in jsdom. A stylesheet assertion is an acceptable minimal regression guard, but a browser viewport check is stronger when already available.

## Endpoint context for shared editors

If one modal edits two resource classes (for example tenant roles and global templates), derive the save endpoint and reload path from the active resource context. Verify:

- the correct endpoint and HTTP method;
- the payload excludes scope fields that do not belong to the resource;
- the matching list is reloaded after save;
- authorization remains enforced by both UI exposure and backend checks.

## Verification sequencing

Run the focused RED/GREEN test first. Then run the canonical full suite, backend suite, typecheck, lint, build, and `git diff --check`. Parallel checks can contend for CPU and cause an unrelated timeout; rerun a timed-out canonical suite alone before classifying it as a regression. Record both the initial timeout and the clean isolated rerun rather than hiding either result.
