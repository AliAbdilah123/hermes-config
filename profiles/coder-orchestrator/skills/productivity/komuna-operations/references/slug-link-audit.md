# Canonical slug link audit (Komuna)

Use when the API returns canonical `program.slug` / `product.slug`, but the website still navigates to old internal IDs such as `prog-yoga` or `prod-yoga-sv`.

## Durable lesson

Do not conclude “the slug fix is done” from API data alone. Verify the full route chain: API DTO → frontend normalized type → route builder/link → built/deployed asset → live click/API response.

## Minimum audit path

1. Confirm canonical API fields exist for the target records:
   - Program detail/list includes `slug`.
   - Product detail/list includes `slug`.
   - Session card APIs include `productSlug` when session cards navigate to product pages.
   - Workspace/dashboard APIs include `programSlug` and scoped manager `productSlug` when dashboard routes are generated from workspace membership.
2. Search frontend route builders for old-ID usage:
   - `program.id`, `product.id`, `programId`, `productId`
   - `/programs/${...}/products/${...}`
   - `/dashboard/programs/${...}`
   - `navigate(`, `to={`, `href={`
3. Patch shared helpers first, then leaf links:
   - shared workspace navigation should prefer `programSlug || programId` and `productSlug || productId`.
   - workspace normalization should accept both camelCase and snake_case slug fields.
   - public product/session links should prefer `slug || id`.
4. Add focused regression tests around the reported old IDs:
   - `prog-yoga` → `balikpapan-coastal-yoga-studio`
   - `prod-yoga-sv` → `sunrise-vinyasa`
5. Verify in this order:
   - focused red/green frontend tests for route hrefs
   - `go test ./...` in `api/v1` if API DTOs changed
   - `npm run build` in `apps/web`
   - rebuild/restart local API service if Go changed
   - deploy built web dist to the nginx-served path
   - curl live API and/or live asset/page to confirm deployed output

## Common hotspots

- `api/v1/dashboard_handlers.go`: `/me/workspace` must expose `programSlug` and manager `productSlug`.
- `api/v1/program_handlers.go`: session card payloads should expose `productSlug`.
- `apps/web/src/types/session-card.ts` and `apps/web/src/lib/api-types.ts`: DTO types must include slug fields or TypeScript will silently push code back toward IDs.
- `apps/web/src/lib/useWorkspace.ts`: normalize snake_case and camelCase fields; match active workspace by either ID or slug.
- `apps/web/src/components/dashboard/workspaceNavigation.tsx`: central manager/admin/member dashboard route builder.
- `apps/web/src/pages/DashboardEntryPage.tsx`: auto-redirect into dashboard should use program slug when available.
- `apps/web/src/pages/ManagerProductSelectorPage.tsx`: manager product picker/auto-redirect should use program/product slug.
- `apps/web/src/pages/program-detail/ProductCard.tsx`: public product and session links should use program/product slugs.
- `apps/web/src/pages/program-detail/SessionProductsSection.tsx` and `SimpleProductsSection.tsx`: pass `programSlug` through to `ProductCard`; otherwise nested sections regress to `programId`.
- `apps/web/src/pages/product-detail/HeroRight.tsx`: product-scoped “see sessions” links should use `product.slug || product.id` for query params.
- `apps/web/src/pages/ProductDetailPage.tsx`: after resolving a product by ID-or-slug, compute `programPath = program.slug || id` and `productPath = product.slug || productId`, then use those for breadcrumbs, guest redirects, child props, and booking modal props. Keep API fetches on the incoming params/canonical IDs as needed.
- `apps/web/src/pages/SessionsPage.tsx`: resolve products by `p.id === productId || p.slug === productId`, then use `programPath` / `productPath` for all rendered links and guest redirects.
- `apps/web/src/pages/AllSessionsPage.tsx`: “buy voucher/package” fallbacks should use `firstSessionProduct.slug || firstSessionProduct.id`.
- `apps/web/src/pages/all-sessions/*.tsx`: session card clicks and booking modal package redirects should use `session.productSlug || session.productId`.

## Pitfalls

- A live API response with correct slugs does not prove the website is fixed; stale route builders may still construct old URLs.
- Do not stop after dashboard routes pass. Public frontend links can still be wrong in ProductDetailPage, SessionsPage, AllSessionsPage, HeroRight, BookingModal, and session-card components.
- `grep` the built/deployed JS for the old internal IDs (`prog-yoga`, `prod-yoga-sv`) and for route-builder patterns after deploy. Passing source tests alone is not enough.
- When replacing `id` / `productId` with slug path variables, do not accidentally use those variables before the product/program data is loaded; API calls at the top of loaders may still need the route params.
- Dashboard/workspace pages may not have access to slug fields unless `/me/workspace` is extended.
- Tests that render whole pages may miss product cards if the current page version renders packages instead; test the leaf link component when appropriate.
- Deployment can fail from filesystem permissions; retry the web dist rsync with `sudo` rather than treating it as a code failure.
