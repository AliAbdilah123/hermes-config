# Full-stack isolated preview pattern

Use when a previewed UI depends on backend changes that are not deployed to production.

## Topology

- SPA: `/previews/<slug>/`
- Preview API: `/previews/<slug>/api/v1/`
- Local API listener: a dedicated loopback port
- Data: copied or sanitized non-production database
- Production API/data: unchanged

## Procedure

1. Build the feature API binary from the isolated worktree.
2. Copy the production-like database to a preview-only path; never point the preview process at production data when migrations or writes are possible.
3. Start the API on `127.0.0.1:<preview-port>` with an explicit preview DB path. Avoid sourcing loosely formatted environment files as shell code; pass only required environment variables.
4. Add an Nginx `location ^~ /previews/<slug>/api/v1/` before the SPA location. Rewrite the preview prefix to `/api/v1/` and proxy to the preview port.
5. Build the SPA with both the preview asset base and preview API base. Also inject matching runtime basename/API globals if the app uses them.
6. Publish with a clean copy into only the exact preview directory.

## Required verification

- Direct loopback API request returns JSON.
- Nginx local-resolve request to preview API returns the same JSON, not SPA HTML.
- Public preview API returns JSON.
- Preview HTML contains the expected router basename and preview API base.
- Hashed JS/CSS return correct MIME types.
- Headless browser renders expected content; `Page not found` and known runtime errors are absent.
- Production assets, API process, and database remain unchanged.

## Pitfalls

- A frontend preview pointing to production API cannot demonstrate backend fixes.
- Nginx prefix precedence matters: declare preview API location before the broader preview SPA location.
- HTTP 200 from an API URL may be production/SPA fallback HTML; assert JSON content, not status alone.
- Do not commit generated API binaries or copied databases. Check `git status` before committing and remove generated artifacts from the index immediately if staged accidentally.
