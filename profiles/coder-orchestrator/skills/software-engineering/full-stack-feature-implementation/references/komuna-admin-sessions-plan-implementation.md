# Komuna admin Sessions plan implementation pitfalls

Use when implementing a previously approved Komuna admin Sessions page plan/review artifact.

## Lessons from manager-picker/session hierarchy work

- Re-read the approved design/plan and checklist every requested behavior before touching live code. Do not implement only the visual hierarchy and omit behavioral requirements like manager picking.
- Before replacing a working Sessions tab, read its complete data-loading path and preserve its resilience semantics—not only its visible behavior. In particular, note `Promise.allSettled` usage, program-response product fallbacks, and session-derived product recovery before moving logic into a new controller.
- Do not compare a route parameter to a DTO foreign key unless they are proven to use the same identifier namespace. Komuna program routes commonly carry canonical slugs while `product.program_id` carries an internal database ID. A `/programs/:slug/products` endpoint is already program-scoped; a redundant client-side `product.program_id === routeParam` filter can silently discard every valid record.
- Regression fixtures for slug-backed routes must deliberately use `routeSlug !== internalProgramId`; fixtures where both equal hide identifier-domain bugs.
- If you accidentally implemented a wrong extra feature and revert it, immediately re-apply any requirements that were part of the approved plan. Reverting the bad diff must not silently remove required plan scope.
- Avoid reporting success from bundle markers alone. Bundle markers prove deployment of strings/classes, not that the UX flow is present in the right route. For this page, verify at least the activation path opens the manager picker UI in addition to grepping markers.
- A successful build and focused mock suite do not prove production data integration. Before declaring success, probe the real scoped products/templates/sessions responses and verify the authenticated production page reports the expected non-zero product count for a known populated program.

## Minimal implementation shape

- Keep product hierarchy dominant: product name/card header is the main visual anchor; session rows are compact supporting rows.
- Remove user-facing `Template` copy. Use neutral copy like `Draft`/`inactive` while keeping internal `template` API names if already present.
- Show max next 5 sessions per product.
- Use a left chevron/icon in the product header for collapse/expand, not right-side `Collapse` text.
- Put product details below the compact sessions as a `See detail` section.
- Manager picker must be included when the approved plan includes it:
  - open before activation when no manager is selected,
  - search managers by name/email,
  - scroll/lazy-render results,
  - show profile picture or initials,
  - single-select only,
  - persist the selected manager on the concrete session,
  - return manager name/image fields in session APIs used by other pages.

## Verification checklist

- Before declaring the plan implemented, reconcile the working tree against every plan task: expected new files, named interfaces, behavioral requirements, and tests. A passing build plus adapted legacy tests is not enough when the plan explicitly requires new model/controller/calendar coverage.
- Run the focused production and prototype suites first, then the full frontend suite separately. If the full suite has an unrelated pre-existing failure, record the exact failing test and still prove the changed scope with green focused tests, lint, and build; do not describe the whole suite as green.
- Backend: migration/idempotent schema adds session manager field when the approved plan requires one; otherwise preserve the existing contract. Run `go test ./...`, backend build, and service health verification.
- Frontend: `env -u VITE_NEON_AUTH_URL npm run build`; deploy fresh Vite assets; verify public bundle has exact markers for `Choose session manager`, `Search managers`, `Assign & activate`, `showing next 5 sessions`, and `See detail`.
- Preserve the standalone prototype route as a regression surface. If production rules intentionally change shared components (for example, deactivation becomes final), update prototype tests to assert the same rule while retaining prototype-only controls and sample-data behavior.
- Prefer browser/UI verification for the actual activation modal when possible; string greps are supplemental deployment evidence only. If browser inspection is unavailable, report that limitation and combine focused interaction tests with public asset/status and bundle-marker checks rather than implying a visual smoke was completed.
