# Frontend-Only Proximity Sort with Static City Coordinates

Use when the backend stores program/venue locations as free-text strings (not lat/lng), has no spatial query support, and the user wants nearest-first sorting when geolocation is granted.

## Pattern

1. **Capture real coordinates** from `navigator.geolocation.getCurrentPosition()` — don't discard the position object.
2. **Build a static city→coordinates map** keyed on the exact location strings in your seed data.
3. **Haversine formula** for spherical distance (good enough for city-level precision).
4. **Sort instead of filter**: show all programs but sorted nearest-first. Push programs with unknown locations ("Online", unmapped cities, null) to the end.
5. **Keep the filter→sort transition clean**: when location is active, `matchesLocation()` becomes a pass-through (all programs match), and the sort step handles relevance.

## Minimal implementation

```typescript
const CITY_COORDS: Record<string, [number, number]> = {
  'Brooklyn, NY': [40.6782, -73.9442],
  'Lisbon': [38.7223, -9.1393],
  // ... all seed locations
}

function haversineMiles(a: [number, number], b: [number, number]): number {
  const R = 3958.8
  const toRad = (d: number) => (d * Math.PI) / 180
  const dLat = toRad(b[0] - a[0]), dLon = toRad(b[1] - a[1])
  const aVal = Math.sin(dLat/2)**2 + Math.cos(toRad(a[0])) * Math.cos(toRad(b[0])) * Math.sin(dLon/2)**2
  return R * 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal))
}

function sortByDistance(programs: ProgramDTO[], userLat: number, userLng: number): ProgramDTO[] {
  const user: [number, number] = [userLat, userLng]
  return [...programs].sort((a, b) => {
    const distA = a.location ? (CITY_COORDS[a.location] ? haversineMiles(user, CITY_COORDS[a.location]) : a.location === 'Online' ? 1e7 : Infinity) : Infinity
    const distB = b.location ? (CITY_COORDS[b.location] ? haversineMiles(user, CITY_COORDS[b.location]) : b.location === 'Online' ? 1e7 : Infinity) : Infinity
    return distA - distB
  })
}
```

## Pitfalls

- **Hardcoded stub trap**: If `matchesLocation('5mi')` was a hardcoded stub returning `p.location === 'Brooklyn, NY'`, it must be changed to pass-through when switching from filter to sort. Otherwise the combined filter+sort is just a Brooklyn-only filter with distance sorting (still empty for non-Brooklyn users).
- **Coordinates discarded**: The most common bug is `getCurrentPosition(() => setFilter('5mi'))` — the position is thrown away. Capture `pos.coords.latitude` and `pos.coords.longitude`.
- **Online/null programs**: Decide where they sort. "Online" programs typically go after geographic but before unknown. Null/unknown go last.
- **Static map is stale**: When a new program is added with a city not in the map, it sorts last. Upgrade path: add lat/lng columns to the programs table and return them in the DTO.

## Upgrade path

When adding lat/lng to the backend schema and API DTO:
1. Add `latitude` and `longitude` (nullable `real`/`double`) to the programs table
2. Populate for existing rows via migration
3. Expose in `ProgramListDTO`
4. Replace `CITY_COORDS[p.location]` with `p.latitude`/`p.longitude` in the distance function
5. Remove the static map
