# Fail-closed UI release gates

Use for navigation-heavy or whole-product UI changes.

1. A green suite/build is necessary, not sufficient. Compare the final diff to the approved scope surface-by-surface; wrapper classes and a trailing recolor block do not prove material migration.
2. Run independent review before commit/deploy. Fail only on concrete correctness, accessibility, or scope blockers; leave browser-only visual polish for E2E.
3. When one transition fails, audit every sibling transition: all History API calls, async route loaders, selectors, tabs, and authenticated early-return routes.
4. Make async navigation transactional: load required data first, then commit view/data/URL together. On failure preserve or restore the last successfully rendered state and URL.
5. Separate visual active section from exact-route duplicate detection. A detail route may highlight its parent while still needing Board and parent-list navigation.
6. Exercise controls, not presence: click account actions on early routes; test selector/tab/detail success and failure; assert rendered data and URL coherence.
7. Inventory direct `pushState`/`replaceState` calls and state mutations before awaited requests. Centralize URL commits when practical so rollback tracking cannot drift.
8. After the last fix rerun the complete suite, production build, diff check, and warning scan. Treat React warnings from production markup (for example missing list keys) as findings even if tests pass.
9. Commit/push/deploy only after review passes, then run authenticated public E2E at required desktop and mobile viewports, checking overflow, focus, dialogs, notifications, and real navigation.
