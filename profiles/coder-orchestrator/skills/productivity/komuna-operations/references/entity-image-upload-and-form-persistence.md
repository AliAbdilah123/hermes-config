# Entity image upload and form persistence

Use this playbook when adding editable Program, Product, or Package images to Komuna's active Go + SQLite API and React frontend.

## Reuse the existing contract first

Before adding schema:

- Inspect `api/v1/schema.go`, DTO helpers, query scanners, and `apps/web/src/lib/api-types.ts`.
- Komuna may already have `image_url` columns and read-side `imageUrl` fields while create/update handlers and forms silently drop them.
- Prefer extending existing writes and row mappers; do not add a media table or migration unless image metadata is genuinely required.

## Backend upload boundary

Use one scoped multipart endpoint and return a root-relative `imageUrl`; keep the existing entity mutations JSON-based.

Required properties:

- Apply `http.MaxBytesReader` for a hard request cap; `ParseMultipartForm` alone is only a memory threshold.
- Accept JPEG, PNG, GIF, and WEBP. Validate file signatures, and require both `RIFF` and `WEBP` markers for WEBP. Reject SVG user uploads.
- Generate server-side random/versioned filenames; never derive storage paths from client filenames.
- Write to a temporary file, sync/close, then atomically rename.
- Use an absolute upload root (configured or derived from the DB directory), not a working-directory-relative path.
- Verify the program exists and the target Product/Package belongs to that program before writing any bytes.
- Admin can manage program-scoped images. Product Manager access must be checked against the existing assigned Product; Package scope must resolve through package entries to an assigned Product.
- Serve `/uploads/` in both the Go handler and production nginx. A returned URL is not successful until it returns HTTP 200 publicly.

## Tri-state persistence

Image mutations need three states:

1. Field omitted: preserve existing image.
2. String: replace image.
3. Explicit `null` (or the agreed clear value): remove image.

In Go, `*string` cannot reliably distinguish omitted JSON from explicit `null`; use `json.RawMessage`, a custom optional type, or map presence checks.

### Package versioning

Komuna Package edits create a new immutable version. If `imageUrl` is omitted, copy the predecessor's image into the replacement row. If explicitly replaced or cleared, affect only the new version; leave the historical predecessor unchanged.

## Frontend integration

Use one small controlled `ImageField` across Program Settings, Product create/edit, and Package create/edit:

- Program thumbnail appears immediately above Program name.
- Add `imageUrl` to Product/Package row mappers so edit hydration cannot discard it.
- Reset image state on create and hydrate it on edit.
- Use the existing API client's `FormData` support; do not set multipart `Content-Type` manually.
- Provide labeled keyboard-operable choose/replace/remove controls, disabled/uploading states, `aria-live` errors, and a broken-preview placeholder.
- Resolve previews through `publicAssetUrl`.

## Consumer hardening

Audit direct `<img src={imageUrl}>` use. Normalize root-relative, base-relative, and absolute values through `publicAssetUrl`, and add load-error fallbacks. In Komuna this commonly includes:

- Product detail hero
- Session cards (product-derived images)
- Booking modal package choices
- Program gallery/carousel and catalog cards

Preserve existing carousel/gallery semantics and placeholders; this is not a redesign.

## Verification and deployment

1. Add focused backend tests for auth/scope, cross-program IDs, type/signature, malformed WEBP, size cap, and tri-state persistence.
2. Add focused frontend tests for the shared field and each form's hydration/payload behavior.
3. Run all Go tests, focused frontend tests, and a clean frontend build with `VITE_NEON_AUTH_URL` unset.
4. Build the active API binary, restart `komuna-api.service`, and verify health.
5. Deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`.
6. Ensure nginx aliases `/uploads/` to the complete Komuna upload root, not only `/uploads/profiles/`; run `nginx -t` and reload.
7. Verify public SPA asset hashes/feature markers and fetch a real uploaded image URL with HTTP 200.
8. Commit and push only after deployment verification.

## Pitfalls

- Upload-first forms can orphan files when the later entity mutation fails or the user cancels. Clean up known failed uploads; add garbage collection only when measured need justifies it.
- Do not delete the last good file before the replacement file and DB reference succeed.
- Stable filenames can remain stale behind browsers/CDNs; generated filenames avoid this.
- Admin create forms may upload before a Product/Package ID exists. Permit program-scoped upload only for Admin; Product Managers require an existing assigned entity.
- A broad frontend suite may contain unrelated failures. Keep focused changed-scope tests green and report unrelated baseline failures honestly; do not weaken tests to accept both outcomes.
