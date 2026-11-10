# Manual Polygon Authoring

Use this pattern when users must create or correct named map areas themselves.

## Minimal data path

1. Keep checked-in/source geometry immutable.
2. Load user-authored geometry from the app's persistence layer.
3. Render a merged lookup where persisted geometry overrides the same source name.
4. Save GeoJSON `Feature` polygons with coordinates in `[longitude, latitude]` order, even when the map library exposes points as `{lat, lng}`.
5. Close the polygon ring by repeating the first coordinate at the end.

For browser-local prototypes, `localStorage` is sufficient only when device-local persistence is acceptable. Use backend persistence when areas must be shared across users or devices.

## Editor behavior

- Create: ask for a name, let the user tap/click at least three distinct points, render the in-progress polygon, and allow point dragging.
- Edit: load the existing polygon into draggable points and save under the same stable name unless rename semantics are explicitly required.
- Redraw: remove the draft layer and markers without touching the last saved geometry.
- Cancel/close: remove draft layers and leave saved geometry unchanged.
- Reject blank names, non-finite coordinates, and fewer than three distinct points.
- Do not silently coerce line or point geometry into polygons.

## Mobile interaction

Keep the map visible while drawing. Open the area editor as a compact dialog/instruction surface, then dismiss the navigation drawer before map taps begin. Markers need touch-safe dragging. A mobile drawer should use a stable visible trigger, explicit open/close state, and `aria-expanded`/`aria-controls`; avoid state transitions that leave it technically visible but still translated off-screen during immediate checks.

## Focused checks

- Unit-test latitude/longitude conversion, ring closure, validation, and replacement behavior.
- Browser E2E on a phone viewport: open drawer, start area creation, add three map points, save, reopen the area list, verify the new area, open edit, and ensure no page errors.
- Verify source areas still render after custom geometry is added.
- Verify cancel/redraw does not overwrite saved geometry.
