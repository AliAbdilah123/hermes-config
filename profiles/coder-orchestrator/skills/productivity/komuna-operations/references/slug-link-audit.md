# Slug/link audit for Komuna program/product routes

Use when the user reports old/random slugs like `prog-yoga` or `prod-yoga-sv` appearing in URLs after API slug normalization.

## Key lesson

Do not stop at checking `programs.slug` / `products.slug` in the DB or API. The production API may already return canonical slugs while the React app still builds public links from internal IDs.

## Read-only investigation checklist

1. Verify API canonical slugs first:
   - `GET /api/v1/programs`
   - `GET /api/v1/programs/<program-slug>/products`
2. Search frontend route builders for ID-based public paths:
   - ``/programs/${id}``
   - ``/programs/${program.id}``
   - ``/programs/${programId}``
   - ``/products/${product.id}``
   - ``?productId=${product.id}``
   - dashboard paths using `programId` / `productId`
3. Separate API paths from user-visible navigation paths:
   - API calls may still use IDs/slugs accepted by the resolver.
   - Public `<Link>`, `navigate()`, `href`, and redirect URLs should prefer canonical slugs.
4. Inspect DTOs that feed dashboards/workspaces. If `/me/workspace`, platform dashboard rows, session rows, voucher/wallet rows, or package rows expose only IDs, the frontend cannot build canonical links without additional lookup.

## Common Komuna hotspots

- Program detail product cards: `apps/web/src/pages/program-detail/ProductCard.tsx`
- Program detail children receiving `program.id`: `apps/web/src/pages/ProgramDetailPage.tsx`
- Join success redirects: `apps/web/src/pages/program-detail/HeroSection.tsx`
- All sessions cards/modals: `apps/web/src/pages/all-sessions/*`
- Member/dashboard entry routes: `DashboardEntryPage.tsx`, `MemberDashboardPage.tsx`, `dashboard/ProgramsListPage.tsx`
- Shared dashboard navigation: `components/dashboard/workspaceNavigation.tsx`, `ProgramDetailLayout.tsx`, `DashboardShell.tsx`
- Workspace API: `api/v1/dashboard_handlers.go` (`/me/workspace` should expose program/product slugs if dashboard routes should be canonical)
- Platform dashboard API: `api/v1/platform_handlers.go` (program rows need slug if links should avoid IDs)

## Fix shape after approval

- Keep internal DB IDs unchanged; they are foreign keys.
- Add slug fields to backend DTOs that drive navigation (`programSlug`, `productSlug`, or equivalent).
- Add small shared frontend route helpers that use `slug ?? id` for public navigation.
- Preserve old ID routes as compatibility aliases until canonical URLs are fully verified.
- Add tests for links rendered from representative DTOs so future route builders do not regress to IDs.
