# Leaflet runtime assets and responsive map verification

Use this when publishing a Leaflet map that must work reliably across mobile, tablet, and desktop.

## Characteristic failure

Scattered 256px map fragments, large white gaps, tiles overlapping side panels, excessive document height, or horizontal scrolling usually mean Leaflet JavaScript ran but Leaflet CSS did not apply. Without the stylesheet, `.leaflet-pane` and `.leaflet-tile` lose absolute positioning and the map container loses clipping, so tiles participate in normal document flow.

Do not mistake this for missing tile images: failed tile requests create holes inside a correctly positioned grid; missing Leaflet layout CSS creates displaced tiles and document overflow.

## Investigation

1. Inspect a screenshot at phone and tablet/desktop widths.
2. Verify the served page includes the viewport meta tag.
3. Fetch the Leaflet CSS URL and check HTTP status, content type, and body.
4. If `integrity=` is present, compute or compare the actual digest. A CDN can return HTTP 200 while the browser rejects content whose bytes no longer match stale SRI metadata.
5. In a browser, assert:
   - `getComputedStyle(tile).position === "absolute"`;
   - the map has a resolved non-zero height;
   - `document.documentElement.scrollWidth <= innerWidth`;
   - the map stays clipped inside its column.
6. Check CSS parsing, not merely file presence. A malformed/truncated token can cause every rule after it—including media queries—to disappear from `document.styleSheets[n].cssRules`.
7. Compare selector specificity. An earlier `.history { display:flex }` can beat a later mobile `.history { display:none }` when declarations have equal specificity and source parsing/order is not what was assumed; use a deliberate selector such as `.shell > .history` and verify computed display.

## Durable asset strategy

For small static applications, vendor the exact Leaflet CSS and JS files and serve them from the same origin. Version their URLs when updating. This removes runtime dependence on CDN availability and stale integrity metadata. Keep OpenStreetMap tile requests separate; attribution and tile-provider usage policy still apply.

If using a CDN intentionally, pin the exact version and verify the current SRI digest from the served bytes before deployment.

## Regression checks

Leave a browser test that runs at representative desktop and phone viewports and checks:

- Leaflet layout CSS is active (`position:absolute` on a synthetic or live `.leaflet-tile`).
- No horizontal document overflow.
- Desktop columns preserve the intended ratio within tolerance.
- Mobile side panel/drawer starts hidden, opens, and closes.
- Map overlays/polygons exist even if external tile image requests are temporarily unavailable.
- Any region list action closes the mobile drawer and fits/opens the selected polygon.
- No page errors are emitted.

Do not make the E2E gate depend exclusively on successful third-party tile downloads. External image throttling or transient DNS failures can obscure whether the application layout and polygon layer are correct. Test tile transport separately from application structure.

## Publication discipline

After source changes, verify the full chain: source asset → deployed directory → public HTML asset URL → computed browser styles. Cache-bust stylesheet and script URLs after fixes. A local pass is not a public pass; if public browser verification is blocked by CDN/security behavior, report that boundary precisely instead of calling the release fully verified.
