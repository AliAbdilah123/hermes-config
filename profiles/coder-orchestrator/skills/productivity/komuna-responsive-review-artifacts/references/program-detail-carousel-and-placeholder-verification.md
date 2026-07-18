# Program-detail carousel and missing-image verification

Use this checklist when a Komuna review prototype or live implementation includes a Program/Product/Package gallery.

## Preserve interaction semantics

- A design labeled **carousel** must render one active slide at a time, not a multi-image grid.
- Include visible previous/next controls, an accessible gallery region, a current/total counter, and a slide label or caption.
- Verify behavior, not just appearance: activate both controls and confirm the active slide and counter change.
- Compare the live implementation against the approved prototype screenshot/component before declaring parity. A visually attractive substitute is still wrong when it changes the requested interaction model.

## Preserve catalog entries when images are absent

Build gallery entries from active Program, Product, and Package records first. Treat each image URL as optional metadata; do not construct the gallery by filtering to records that have truthy URLs.

For each entry:

1. Use its storage URL when it is a valid string.
2. If the URL is absent, malformed, or fails to load, keep the entry and render intentional placeholder artwork.
3. Label placeholders by entity type (`Program`, `Product`, or `Package`) and retain the entity name as the caption.
4. Apply the same fallback rule to catalog-card thumbnails; never leave a blank slot or broken-image icon.

This preserves the Product/Package inventory even before storage assets have been uploaded.

## Data-flow rule

Reuse Program detail and Package responses already fetched by the page. Do not add gallery-specific or duplicate Product requests merely to populate the carousel.

## Regression checks

Leave focused tests that assert:

- the gallery region exists;
- previous and next buttons exist;
- the counter renders and changes after navigation;
- missing catalog image URLs produce labeled placeholders;
- a valid storage image URL is rendered;
- no extra gallery/Product fetch occurs;
- archived Products and Packages remain excluded.

Before deployment, run focused tests, scoped lint, a production build, and desktop/mobile visual QA. Visual QA must explicitly check carousel controls/counter and Product/Package placeholders—not merely clipping and alignment.
