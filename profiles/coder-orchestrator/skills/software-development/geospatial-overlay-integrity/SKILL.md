---
name: geospatial-overlay-integrity
description: Diagnose, implement, and verify named map overlays whose locations, boundaries, routes, or represented areas are inaccurate. Use for Leaflet/MapLibre/Google Maps polygon, line, point, GeoJSON, and geocoding defects.
---

# Geospatial Overlay Integrity

Use when a map's basemap is correct but named overlays appear in the wrong place, use implausible boundaries, or represent every feature as the same generic shape.

## Workflow

1. **Trace the overlay source before changing styles.** Find the exact path from displayed place name to coordinates and layer construction. Search for guessed centers, fixed coordinate deltas, index-based sizing, and shape generators.
2. **Reproduce and inventory.** Record every currently displayed name and inspect every overlay, not only the first one.
3. **Classify the real feature.** Administrative areas and buildings are polygons; roads are lines; point-only landmarks remain points with an explicit small display radius. Do not force all features into polygons.
4. **Resolve identity carefully.** Validate city, district, street, canonical name, and feature type. Never trust the first same-name geocoder result without checking its full address.
5. **Replace the shared root cause.** Remove the synthetic geometry function and route all affected callers through real geometry. For a small stable set, checked-in GeoJSON is simpler and more reliable than runtime geocoding.
6. **Represent composites honestly.** Use a `FeatureCollection` when one user-facing label intentionally covers multiple real features; do not fabricate a merged boundary.
7. **Render mixed GeoJSON natively.** Use the map library's GeoJSON layer and configure a point renderer. Keep user-facing labels separate from canonical source names.
8. **Describe provenance accurately.** Geographic source geometry is not automatically a live operational/service boundary. Avoid calling roads or point buffers “polygons”; use “area,” “location,” or “geometry” as appropriate.
9. **Verify locally and publicly.** Test all named entries, valid bounds, selection/zoom behavior, runtime errors, desktop/mobile behavior, deployed asset freshness, and the public route.

## Regression Gate

Leave one focused runnable check that enumerates every expected display name and asserts that each maps to a valid GeoJSON `Feature` or `FeatureCollection`. Browser E2E must iterate every overlay and verify valid bounds; checking only that some `.leaflet-interactive` element exists is insufficient.

## Deployment Notes

Cache-bust the entry module or generated assets when static hosting/CDNs may retain an old bundle. Preserve normal web-readable file modes after deployment, then probe the origin and public URL before claiming success.

## Detailed Reference

See [references/placeholder-geometry-replacement.md](references/placeholder-geometry-replacement.md) for the compact diagnosis, data-shape, and verification recipe.
