# Komuna program detail: packages-first public detail page

Use when the user asks to hide products on a Komuna public program detail page and show packages instead.

## Pattern

- The public program page is `apps/web/src/pages/ProgramDetailPage.tsx`.
- Product sections are rendered as:
  - `SessionProductsSection products={program.products}`
  - `SimpleProductsSection products={program.products}`
- The packages/store section is already present as `StoreSection packages={packages}` and is populated by `apiClient.getPaginated<PackageDTO>(/programs/:id/packages)`.
- Smallest safe change: remove the product section imports/render calls, keep `StoreSection` in place.
- The upcoming-sessions title in the right hero column lives in `apps/web/src/pages/program-detail/HeroRightSessions.tsx`; its `displayEyebrow` style controls the visual prominence.

## Test update

`apps/web/src/__tests__/ProgramDetailPage.test.tsx` may still assert product-card behavior (`Saturday Bag Work`, type badges, `View sessions`). When switching to packages-first:

- Mock `apiClient.getPaginated` with a `PackageDTO` list.
- Use `PaginationMetaDTO.total_pages`, not `totalPages`.
- Replace product-card assertions with package/card checkout assertions, e.g. package name visible, product-only card text absent, checkout link points to `/programs/:programId/packages/:packageId/checkout`.

## Verification

- Run the focused page test: `npx vitest run src/__tests__/ProgramDetailPage.test.tsx` from `apps/web`.
- Run `npm run build` from `apps/web`.
- Deploy the Vite `dist/` to the nginx alias path and verify the public bundle no longer contains product-section markers such as `SessionProductsSection`, `SimpleProductsSection`, `sections.sessionProducts`, or `sections.simpleProducts`.
