# Client-Side Filter Hardcoded Stubs

Use when a location/permission-based UI filter shows "no results found" even after the user grants the permission, or when a filter with multiple options always produces the same fixed subset of results.

## Root-cause pattern

A client-side filter function was shipped with hardcoded return values (stubs) during development, and the real implementation was never written. Common signals:

1. **Permission granted but results empty** — `navigator.geolocation.getCurrentPosition()` success callback fires, but the position object is discarded. Only a hardcoded location string is checked.
2. **Filter options produce fixed subsets** — e.g. "5mi" and "25mi" both only match `location === 'Brooklyn, NY'`, "1mi" always returns `false`.
3. **No actual distance/coordinate calculation exists** — the filter compares against a string literal, not computed data.

## Triage checklist

1. **Trace the permission callback** — does it actually capture the permission result data (coordinates, token, etc.) or just flip a UI state?
   - In komuna: `getCurrentPosition(() => setLocationFilter('5mi'))` — position was ignored.
2. **Inspect the filter function body** — look for hardcoded literals (strings, booleans) in switch/case or if/else that don't reference actual data.
   - In komuna: `case '5mi': return p.location === 'Brooklyn, NY'` — hardcoded city string.
3. **Check for missing data dependencies** — if the filter needs coordinates, does the data model have them? The fix may need a static lookup map (city→lat/lng) if the backend only stores location as text.
4. **Decide: filter or sort?** — The user may want filtering (exclude far programs) or just sorting (show all, nearest first). Clarify before implementing.

## Fix pattern

1. Capture permission data fully (coords, not just "granted").
2. Add a static geocode map for known location strings (city name → [lat, lng]) if the backend doesn't store coordinates.
3. Implement Haversine distance calculation.
4. Wire distance to the filter: `dist <= radius` instead of `location === 'HardcodedCity'`.
5. Add a fallback: if user coordinates aren't available yet, pass all programs through (don't show empty state while geolocation is pending).

## Haversine reference (TypeScript)

```ts
function haversineMiles(a: [number, number], b: [number, number]): number {
  const R = 3958.8
  const toRad = (d: number) => (d * Math.PI) / 180
  const dLat = toRad(b[0] - a[0])
  const dLon = toRad(b[1] - a[1])
  const lat1 = toRad(a[0]), lat2 = toRad(b[0])
  const aVal = Math.sin(dLat/2)**2 + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2
  return R * 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal))
}
```

## Pitfalls

- A city ~5 miles from a downtown reference point can fail a 1-mile radius test. Use the city's actual coordinates as the user location for tests, not a nearby metro center.
- "Online" programs should pass through all distance filters (no geographic constraint).
- Programs with unknown locations (not in the static map) should be excluded from distance filters — Infinity > any radius.
- The sidebar/pill label should reflect the active filter dynamically, not show a hardcoded default like "5mi ▾".

### i18n/locale files as hardcoded text

When the user reports a specific text string (e.g. "Brooklyn, NY") still appearing in the UI after code cleanup, and searching component source files returns nothing — **check translation/locale files**. Text rendered via `t('key.path')` may be embedded in `i18n/en.json`, `i18n/id.json` (or equivalent locale JSON/YAML) and silently survive all code-level fixes.

Triage pattern:
1. Grep component code for the text → nothing found
2. Grep all project files for the text → hits in `i18n/*.json`
3. Translation keys like `"summary": "Brooklyn, NY"` under `discovery.location` render via `t('discovery.location.summary')`

Fix: either delete the stale locale key (if component no longer uses it), update it to a generic value ("Nearby"), or remove the component's usage of the key entirely.
