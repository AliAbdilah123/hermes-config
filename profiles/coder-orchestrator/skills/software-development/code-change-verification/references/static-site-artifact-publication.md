# Static-site artifact publication

Use when source changes must become visible on an existing nginx/static-hosted public site.

## Release sequence

1. Locate the exact server block and document root. Do not assume the repository directory is live.
2. Compare source HTML with public HTML or hashes. HTTP 200 proves availability, not freshness.
3. Run focused/full checks and commit the intended files.
4. Copy the artifact to the real document root, excluding repository-only files and preserving web-readable file/directory modes.
5. Version changed CSS/JS entry URLs when browser or CDN caching may retain old assets.
6. Fetch public HTML and assert stable feature markers and new asset versions.
7. Run the exact desktop/mobile interaction against the public URL. Only then call it deployed or publicly verified.

## Reporting states

- **Implemented:** code exists and local checks pass.
- **Deployed:** the live document root contains the new artifact.
- **Publicly verified:** public browser E2E exercised the requested behavior.

Never present a local commit plus an unchanged public HTTP 200 as a visible release. If no Git remote exists, report that separately; a missing remote does not prevent filesystem deployment when nginx serves a local document root.

## Asset pitfall

Leaflet's default marker icons depend on image paths. For a self-contained static editor, either deploy those images or use `L.divIcon` with local CSS. Confirm public browser logs contain no missing marker assets.