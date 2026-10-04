# Browser-tab branding from an existing CSS logo

When the product logo is rendered in components rather than stored as an image, reuse its established shape, letter, and brand tokens in a minimal standalone SVG favicon instead of adding a dependency or inventing new branding.

## Minimal workflow

1. Inspect the primary navigation/header logo and shared CSS brand tokens. Confirm the canonical letter, **typeface/weight**, background, foreground, corner radius, and product naming; sibling pages may contain stale variants.
2. Create a tiny SVG in the frontend root or existing public-assets location using those values. Keep it dependency-free and scalable with `viewBox`. For a lettermark, do not silently substitute a generic font: an Arial `c` is not the same logo as a Fraunces `c`. Because external SVG favicons cannot reliably load the app's bundled webfont, convert the canonical glyph from the already-installed font file to SVG path data (for example with a temporary `uv run --with fonttools --with brotli` script using `TTFont` and `SVGPathPen`). This keeps the favicon self-contained and browser-independent without adding a project dependency.
3. Add the native HTML declaration beside the document metadata:
   ```html
   <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
   ```
4. Run the production frontend build. Inspect generated `dist/index.html`: Vite may fingerprint an imported root favicon into `dist/assets/favicon-<hash>.svg` instead of copying it as `dist/favicon.svg`.
5. If source is already correct and pushed but the public favicon is missing or stale, treat it as a deployment gap rather than making another source edit. Deploy the complete frontend `dist/` to the configured nginx document root.
6. Verify through both origin and the public hostname: extract the favicon URL from served HTML, fetch that exact URL, require `200` with the expected image content type, and byte-compare it with the source asset when practical. Account for nginx `sub_filter` rewriting a project-prefixed build path to a root-mounted public path.
7. Run `git diff --check`, inspect the narrow diff, and commit only the favicon and HTML declaration when a source change was actually needed. Preserve unrelated working-tree changes.

## Pitfalls

- `<title>` only controls tab text; the logo beside it is a favicon declared with `<link rel="icon">`.
- Do not treat the first logo-like occurrence as canonical. Compare the active landing/header brand against older legal/about/auth variants.
- Do not add React code for static browser metadata.
- Do not stop after matching only the colors and rounded rectangle. Rasterize the final SVG at a large size and visually compare the actual letterform to the canonical in-app mark or supplied reference before deploying; generic sans-serif text can look uppercase or materially different at favicon size.
- Prefer path data over `font-family` for distinctive lettermarks. A named webfont in a standalone favicon may fall back because the favicon does not inherit the page's loaded fonts.
- Do not assume the source URL (`/favicon.svg`) survives the build unchanged; inspect generated HTML and verify its emitted fingerprinted asset.
- Do not create a duplicate commit when `HEAD`, `origin`, and source already contain the correct mark. A public 404 in that state usually means the built frontend has not been published.
- Do not claim a live deployment unless the exact favicon referenced by public HTML was fetched and checked; build + push proves source delivery only.
