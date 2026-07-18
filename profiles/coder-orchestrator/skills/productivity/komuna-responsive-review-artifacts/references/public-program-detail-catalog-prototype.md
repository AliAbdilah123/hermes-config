# Public Program Detail Catalog Prototype

Use this pattern when proposing a Komuna public Program Detail redesign that changes which catalog content appears below the hero.

## Inspection first

Trace the real `/programs/:id` composition before drawing:

- page render order;
- existing hero component and responsive CSS;
- section being removed or replaced;
- actual product, package, and session-card components;
- canonical slug/ID link behavior.

A card component may exist without a corresponding section component. Record that distinction.

## Fidelity and correction hierarchy

Start with the existing hero tokens, typography, chips, CTA, and stats. Reuse actual ProductCard and PackageCard vocabulary unless the user explicitly asks those cards to adopt another live component's design.

If the user requests “make these look like the current session cards,” inspect `SessionCardCompact` and copy its geometry literally:

- compact horizontal row;
- 4:3 media at left;
- content column with `min-width:0`;
- concise metadata;
- pill primary action;
- current border, radius, padding, and responsive collapse behavior.

Do not merely make vertical cards shorter and call them session-like.

## Catalog composition and alignment

For Products + Packages below the hero:

- remove the session-instance rail from the proposed composition;
- keep Products and Packages adjacent on desktop and stacked on tablet/mobile;
- preserve product-detail/session and package-checkout affordances;
- baseline-align each section heading with its count;
- use the same media dimensions, card inset, content gap, and action treatment in both columns;
- top-align media and content rather than independently centering them;
- place actions according to the requested axis: use `margin-top:auto` only for bottom actions; when actions belong on the right, give the body an explicit `minmax(0,1fr) max-content` information/action grid and vertically center the action column;
- stack multiple actions inside that right-side column, keeping information top-left aligned and preventing action labels from wrapping;
- do not combine right-side actions with forced `height:100%` or arbitrary `min-height`: let media/content determine compact card height, otherwise a large empty band appears beneath both information and actions;
- on narrow mobile screens, keep a compact media/info row (about 88px square media), move actions below the info within the info column, hide nonessential secondary actions if necessary, and reduce hero/gallery/catalog spacing before shrinking readable text or touch targets;
- keep the unmatched cell empty when counts differ rather than inventing content;
- separate Product from Package commerce semantics: Product cards may omit cost when requested, while Package cards retain the purchasable package price;
- wire prototype actions to the real route contract rather than `#`: product detail `/programs/{program}/products/{product}`, filtered sessions `/programs/{program}/sessions?productId={product}`, and checkout `/programs/{program}/packages/{package}/checkout`.

Independent vertical lists can drift when one package row is taller than its product peer. When strict cross-column row alignment matters, use one shared outer two-column grid so each product/package pair occupies the same grid row and stretches to the taller card. Do not fix this with arbitrary per-card heights.

## Hero gallery variant

When the user asks for a program gallery beside hero text and CTAs:

- switch the hero to a two-column layout: copy/CTAs left, gallery right;
- keep both columns vertically aligned and give the gallery a reserved aspect ratio;
- include accessible previous/next buttons, slide dots, image count, and meaningful captions/alt text;
- use real program images in implementation; tone placeholders are acceptable only in a static prototype;
- do not autoplay unless requested;
- stack mobile in this order: hero copy, CTAs, gallery, catalog.

A split hero narrows the text column. Re-test existing stats and CTAs immediately: a four-column stats row and wrapping CTA labels can collide. Prefer a two-column stats grid in the narrowed copy column and `white-space:nowrap` for short CTA labels; verify at desktop and mobile widths.

## Visual verification loop

1. Publish the artifact at mode `0644` with a fresh cache-busting query.
2. Assert the public HTML contains `viewport`, `Products`, and `Packages`; include gallery markers when applicable.
3. Capture a screenshot tall enough to show the complete hero and at least two paired catalog rows.
4. Inspect exact defects, not only overall aesthetics:
   - heading/count baselines;
   - paired row top edges and heights;
   - media top edges and dimensions;
   - title, price/unit, and action baselines;
   - lower-page empty space caused by unequal counts;
   - hero stat collisions and CTA wrapping;
   - overlap, clipping, and horizontal overflow.
5. Correct visible issues and capture again. Do not declare visual verification complete when the screenshot still shows a major overlap.
6. Keep mobile breakpoints that prevent page-wide horizontal overflow.
7. Commit and push the canonical artifact after verification.

A screenshot ending mid-card can be normal viewport continuation; distinguish it from actual component clipping.

## Scope boundary

A prototype request changes only the review HTML artifact. Do not modify the live React page, API fetches, routing, or deployment behavior without explicit implementation approval.
