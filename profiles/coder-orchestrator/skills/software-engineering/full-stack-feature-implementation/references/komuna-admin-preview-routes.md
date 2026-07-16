# Komuna Admin Preview Routes

Use this when adding admin preview actions for member-facing products/packages.

## Pattern

- Add icon-only admin table actions (`Preview`, `Edit`, `Archive`) using accessible labels and tooltips (`aria-label`, `title`).
- Use slug-first URLs with ID fallback:
  - `/dashboard/programs/:programSlug/products/:productSlug/preview`
  - `/dashboard/programs/:programSlug/packages/:packageSlug/preview`
- Keep DB IDs canonical internally; resolve `slug || id` only at navigation/fetch boundaries.
- Reuse member-facing components rather than duplicating display logic.

## Preview UX

- Render previews inside a smaller bordered preview window, not as a full-width normal page. This makes the admin context obvious.
- Make preview content non-interactive:
  - block/cancel clicks on links and buttons inside the preview surface,
  - disable checkout/pay actions explicitly,
  - change CTA copy to preview-safe text such as `Preview only — checkout disabled`.
- Product preview can reuse `ProductDetailPage` with an `adminPreview` prop and an admin banner.
- Package preview should represent the member checkout page, not only the package card. A useful layout is a responsive collage:
  - existing `PackageCard`,
  - checkout `PackageSummary`,
  - checkout `OrderSummaryCard` in preview mode.

## Mobile/responsive requirements

- The preview window should use `width:min(100% - 16/32px, maxWidth)` and `min-width:0` for grid children.
- Collapse collage grids to one column under tablet/mobile widths.
- Remove sticky checkout positioning inside the preview window (`position: static`) so the embedded checkout card does not behave like the real page.

## Verification

- Run the web build and focused page tests.
- Deploy the Vite dist to the active nginx path.
- Verify public bundle markers for preview copy/classes and a direct preview URL returning 200.
