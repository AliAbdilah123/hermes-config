# Placeholder Geometry Replacement Recipe

## Symptom pattern

- Correct map tiles, incorrect overlays.
- Every named place appears as a similarly shaped pentagon/rectangle.
- Shapes are centered on hardcoded coordinates and vary by array index.

That pattern usually means the app is generating demo geometry rather than displaying geographic data.

## Investigation

1. Extract the exact place labels from the announcement/API response.
2. Find their layer constructor and all callers.
3. Look for helpers resembling `polygon(lat, lng, i)` with a fixed `d` offset.
4. Query a geographic source for each label and inspect full address plus returned geometry type.
5. For ambiguous or missing search results, try the canonical local name/address and verify independently before accepting it.

## Data model

Keep a stable map from the displayed label to GeoJSON:

```js
export const regionGeometries = {
  "Named district": { type: "Feature", geometry: districtPolygon, properties: {} },
  "Named road": { type: "Feature", geometry: roadLine, properties: {} },
  "Named landmark": { type: "Feature", geometry: landmarkPoint, properties: {} },
  "Combined area": { type: "FeatureCollection", features: [areaA, areaB] }
};
```

Render through the library's GeoJSON layer. For points, use a small circle radius chosen only for visibility; do not describe that circle as the landmark's true boundary.

## Verification

A focused unit check should compare the geometry-map keys to the expected labels and validate every top-level GeoJSON type. Public browser E2E should iterate all labels, click each entry, assert finite/non-empty bounds, and collect runtime errors. Run at desktop and mobile sizes.

## Deployment trap

A recursive copy may preserve restrictive source modes (for example an owner-only HTML file), causing nginx `403` even though deployment completed. After publishing a static site, normalize directories to `755` and files to `644`, then verify both the origin virtual host and cache-busted public URL. Treat this as deployment hygiene, not a map fix.
