# Komuna Product Detail Mobile Session Cards

Use when the public Komuna product detail page (`/programs/:id/products/:productId`) has unreadable or overflowing upcoming session details, especially in the hero right column.

## Fix pattern

1. Patch the existing product detail hero instead of redesigning the page:
   - `apps/web/src/pages/product-detail/HeroSection.tsx`
   - `apps/web/src/pages/product-detail/HeroRight.tsx` if content/behavior changes are needed
   - shared responsive CSS in `apps/web/src/globals.css`
2. If asked to remove hero CTAs for session products, remove only the session-hero action buttons from `HeroSection`; keep simple-product/store CTAs intact.
3. For `SessionCardCompact` inside product detail hero, prefer CSS overrides at responsive breakpoints:
   - at tablet widths, reduce image column and move the action column to a full-width row (`grid-column: 1 / -1`)
   - at phone widths, shrink the image column further, reduce gaps/padding, and keep booking/status controls visible
   - preserve `minmax(0, 1fr)`, `min-width: 0`, ellipsis, and wrapping instead of adding JS
4. Update focused tests, e.g. assert the removed hero button labels are absent for session products.
5. Build with `unset VITE_NEON_AUTH_URL; npm run build`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, then verify the public JS/CSS hash and bundle markers.
6. Run a multi-viewport check (1440, 768, 414, 375, 320) for the public product URL and assert `documentElement.scrollWidth === clientWidth`. Also confirm removed hero button labels are not present in the rendered button list/bundle.

## Pitfalls

- `SessionCardCompact` is shared by multiple session rails; keep selectors scoped to safe structural breakpoints and visually/programmatically verify no horizontal overflow.
- The product detail right-column cards can overflow even when page-level `scrollWidth` is zero; inspect both the viewport overflow and visible button/detail readability.
- Public product URLs often need slug paths from the local SQLite data; use a real session product URL for the smoke check.
