# Verifying data-backed SPA previews

Use when preview UI depends on API fields, schema changes, uploaded media, or writes not yet supported by production.

## Contract

A feature bundle pointed at the production API is not a valid preview of a new data-backed feature. Conditional controls can disappear, writes can fail, and profile/media fields can be absent while compilation still passes.

## Verification sequence

1. Inventory every requested UI element gated by new response fields.
2. Run the feature API on a dedicated localhost port with an isolated database. For realistic state, copy production SQLite data; never let preview writes touch production.
3. Add a preview-specific Nginx API location before the SPA location and proxy it to the preview API.
4. Inject that exact preview path as `window.__API_BASE__`; do not leave `/api/v1` targeting production.
5. Keep referenced uploads read-only and reachable when the copied database contains their paths.
6. Verify both origin and public cache-busted output:
   - HTML contains preview basename and preview API base;
   - API probe returns JSON (an unauthenticated 401 JSON response is valid routing evidence; HTML or 404 is not);
   - assets have real JS/CSS MIME types;
   - authenticated API response contains each new field;
   - rendered UI visibly shows each requested control and media item.
7. Compare origin-host HTML with public HTML before editing source again; edge caching can preserve an old API-base injection.

## UI checks learned from conditional booking cards

- Never hide a feature’s only entry point because returned arrays are empty. Keep the action visible and show explicit empty states after expansion.
- Assert visible domain wording, not only internal field names.
- Identity UI needs role label, name, resolved image URL, accessible alt text, and initials fallback for absent or failed images.
- Test list and update API responses separately; a list response can be correct while the post-save response drops the new field.
