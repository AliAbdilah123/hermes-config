# Canonical slug link audit for SPA routes

Use this when a page works with an old/internal route identifier but visible anchors still show stale slugs or IDs.

## Pattern

A backend may intentionally accept both canonical slugs and stable internal IDs for backwards compatibility. That can hide a frontend bug: route handlers resolve correctly, but links keep reusing the incoming route param (`id`) or DTO IDs (`program.id`, `product.id`) instead of the canonical display slug.

## Investigation recipe

1. Verify data first: compare `id`, `name`, and `slug` for the reported program/product/package in the DB or API response.
2. Find working reference pages that already compute canonical paths, e.g. `const programPath = program.slug || id` and `const productPath = product.slug || productId`.
3. Audit route builders and props, not just `<Link>` text:
   - `to={\`/programs/${id}...\`}`
   - `navigate(\`/programs/${id}...\`)`
   - child props like `programId={program.id}` or `programId={id}` passed into link-building components
   - redirect components that preserve params from legacy routes
4. Check subpages inside the same program: detail page, upcoming sessions rail, all-sessions page, product cards, package/store links, checkout breadcrumbs, wallet/member-dashboard booking links, booking modals, and legacy redirects.
5. Separate API lookup identifiers from public URL identifiers. API calls can keep using the current param; visible/user-facing links should prefer `slug ?? id`.
6. If a DTO only exposes IDs, extend it with slug fields instead of guessing slugs client-side.
7. Add regression tests that render a fixture where `id !== slug` and assert public anchors do not contain `/programs/<internal-id>`.

## Fix shape

Add or reuse tiny path helpers at the frontend boundary:

```ts
const programPath = program.slug || program.id
const productPath = product.slug || product.id
```

Then pass the canonical path to link-building children. Keep backend compatibility for old IDs/slugs so existing bookmarks keep resolving.
