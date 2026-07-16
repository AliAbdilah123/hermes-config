# Komuna admin product/package preview pattern

When adding admin previews for product/package inventory pages:

- Prefer icon-only action buttons in dense admin tables, but keep accessibility: `aria-label`, `title`/tooltip, clear disabled/loading states.
- Use slug-first routes for preview URLs, with ID fallback from the row DTO:
  - Product: `/dashboard/programs/:programSlugOrId/products/:productSlugOrId/preview`
  - Package: `/dashboard/programs/:programSlugOrId/packages/:packageSlugOrId/preview`
- Keep database IDs as canonical internally. Resolve `slug || id` at route/link boundaries; backend lookup should accept id or slug where possible.
- Do not duplicate public/member-facing UI. Add an admin preview shell/banner and reuse the same member-facing detail/card components so previews cannot drift from real member experience.
- Admin preview shells should include: “Admin preview” context, back link to the admin list, and a short note that checkout/booking actions still follow member rules or are preview-only if deliberately disabled.
- For packages, if no full public package-detail route exists yet, reuse the existing member-facing `PackageCard`/store component first rather than building a separate speculative package detail page.
- Verify with frontend build, targeted tests for affected pages, deployed bundle markers for `/preview` and “Admin preview”, then commit/push.
