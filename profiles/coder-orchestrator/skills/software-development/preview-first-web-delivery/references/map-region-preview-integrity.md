# Map-region preview integrity

Use when a map UI must show affected areas, service zones, districts, or outage regions rather than points.

## Geometry truth

- A polygon-like shape drawn for visual composition is a **mock shape**, not curated or verified geography.
- Do not label synthetic shapes as verified regions, and do not claim that named places have been mapped accurately.
- Before implementation, identify the geometry source for every named region: licensed open boundary data, an authoritative supplied file, or a human-reviewed manual trace.
- Store provenance with each geometry: source URL/file, license note, review state, and last-reviewed time when available.
- If a named place has no defensible boundary, show it as unresolved rather than inventing a polygon.
- Distinguish clearly between static design preview geometry, implementation seed geometry, and production-approved boundaries.

## Design artifact verification

A successful write or HTTP 200 is not enough. After each edit to a standalone HTML design artifact:

1. Check that the served byte count is plausible and did not unexpectedly shrink.
2. Validate the document still contains closing `</style>`, `</body>`, and `</html>` tags.
3. Verify exact visible markers for the main layout and the newly requested change.
4. Render the public URL at desktop and mobile widths when browser tooling is available.
5. Check page text, major element visibility/geometry, and console errors.
6. Use a cache-busted URL after republishing.

When the user says the design shows nothing, inspect source → deployed file → public response body first. Rebuild the complete artifact if it was truncated; do not keep layering patches onto a malformed one.
