# Komuna admin Sessions plan implementation pitfalls

Use when implementing a previously approved Komuna admin Sessions page plan/review artifact.

## Lessons from manager-picker/session hierarchy work

- Re-read the approved design/plan and checklist every requested behavior before touching live code. Do not implement only the visual hierarchy and omit behavioral requirements like manager picking.
- If you accidentally implemented a wrong extra feature and revert it, immediately re-apply any requirements that were part of the approved plan. Reverting the bad diff must not silently remove required plan scope.
- Avoid reporting success from bundle markers alone. Bundle markers prove deployment of strings/classes, not that the UX flow is present in the right route. For this page, verify at least the activation path opens the manager picker UI in addition to grepping markers.

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

- Backend: migration/idempotent schema adds session manager field; `go test ./...`; backend build; service restart health.
- Frontend: `env -u VITE_NEON_AUTH_URL npm run build`; deploy fresh Vite assets; verify public bundle has exact markers for `Choose session manager`, `Search managers`, `Assign & activate`, `showing next 5 sessions`, and `See detail`.
- Prefer browser/UI verification for the actual activation modal when possible; string greps are only a supplemental deployment check.
