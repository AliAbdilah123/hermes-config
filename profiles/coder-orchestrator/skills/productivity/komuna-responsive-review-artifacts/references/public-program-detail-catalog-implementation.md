# Public Program Detail Catalog Implementation

Use after the adjacent Products + Packages prototype is explicitly approved for the live Komuna React page.

## Data and request discipline

- Reuse `ProgramDetailDTO.products` from `GET /programs/:id`; do not add a duplicate products request.
- Packages remain a separate existing request through the established API client.
- Build gallery candidates from already-loaded `program.imageUrl`, active Product images, and active Package images. Do not invent `/gallery` or `/images` endpoints.
- If the approved composition removes session instances entirely, remove the Program Detail preview-session request as well. Preserve session booking behavior on the dedicated Sessions/Product surfaces rather than keeping dead page state.
- Keep voucher-summary requests only when a remaining Program Detail workflow consumes them; remove the request with the removed booking modal, not merely its rendering.

## Route contracts

Prefer API-returned slugs with ID fallback for visible routes:

- Product detail: `/programs/{programSlugOrId}/products/{productSlugOrId}`
- Filtered sessions: `/programs/{programSlugOrId}/sessions?productId={productSlugOrId}`
- Package checkout: `/programs/{programSlugOrId}/packages/{packageSlugOrId}/checkout`

Test actual rendered `a[href]` values with realistic DTOs containing both IDs and slugs. Accessible names may include the Product name (for example, `View Sunrise Vinyasa details`), so focused tests should query the real accessible label rather than only the visible two-word text.

## Shared-card implementation

- Product and Package cards must share compact horizontal geometry, not only a class name.
- Remove legacy PackageCard inline `flex-direction:column`, full-width media, padding, and aspect-ratio styles when applying the compact shared class; inline styles otherwise override the approved CSS and silently retain the old vertical card.
- Keep information top-left and actions in an explicit right column on desktop.
- Product cards omit prices; Package cards retain package price and concise included-benefit copy.
- Avoid forced `height:100%` and arbitrary `min-height` beyond the media-driven compact baseline.

## Asset-path and failure handling

Komuna API image values may be root-relative (`/program-images/...`) while the SPA itself can be built with a subpath `BASE_URL`. A generic asset helper must preserve root-relative paths instead of prepending the SPA base. Relative paths without a leading slash can still be resolved under `BASE_URL`.

Add a focused utility regression test for this distinction. Also add `onError` behavior:

- Product/Package cards replace failed images with the existing tone/placeholder surface.
- Gallery removes failed candidates rather than showing broken-image icons or reserving large blank slots.

Do not trust HTTP 200 alone for media: an SPA fallback can return `text/html` for a missing `.svg`. Verify `Content-Type`, then inspect a deployed screenshot for broken-image icons/alt text.

## Verification sequence

1. Write failing page/card/asset tests first.
2. Run focused Program Detail, ProductCard, and asset-helper tests.
3. Run scoped ESLint on touched files; repository-wide lint may have unrelated debt.
4. Build with `VITE_NEON_AUTH_URL` absent.
5. Deploy fresh `dist/` and verify new asset hashes plus local-auth bundle markers.
6. Smoke the existing Program and Package API paths. Assert no new Product/gallery request in tests.
7. Capture desktop and mobile screenshots.
8. Inspect for hero top whitespace, nested gallery scrolling, failed images, card geometry overridden by inline styles, clipping, and action alignment.
9. Correct visible blockers and capture again before committing/pushing.

## Common traps

- A successful build does not prove the Package card adopted the compact geometry.
- A successful image request with status 200 may actually be the SPA HTML fallback.
- A gallery `max-height` plus `overflow:auto` creates an unnecessary nested scrollbar and clipped image fragments; let the gallery size naturally unless the design explicitly calls for scrolling.
- Reusing the old full-viewport hero `min-height` in a split composition creates a large empty band. Remove forced viewport height and center the two columns naturally.
