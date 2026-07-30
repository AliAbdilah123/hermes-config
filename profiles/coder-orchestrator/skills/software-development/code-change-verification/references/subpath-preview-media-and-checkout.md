# Subpath preview media and checkout verification

## API-hosted uploads

Treat API-returned `/uploads/...` paths as API-hosted media, not SPA-public assets. When the runtime API base is `/previews/<slug>/api/v1`, resolve media beneath `/previews/<slug>/uploads/...` and add a preview-specific Nginx proxy before the SPA fallback:

```nginx
location ^~ /previews/<slug>/uploads/ {
    proxy_pass http://127.0.0.1:<preview-port>/uploads/;
}
```

An upload-form preview proves only the form path. Public cards and detail pages are often separate consumers with a static-public resolver that silently points `/uploads/...` at the production app base. Audit every applicable surface: program product cards, product hero/detail, package cards, checkout/package chooser, and session cards inheriting product media. All API-hosted uploads must use the preview API-aware resolver.

For attendee pictures, trace the whole contract: SQL joins the profile field, scanner emits it, DTO types it, view-model mapping preserves it, and the avatar resolves it. Initials are only an image-error fallback.

Verification must include:

1. One real uploaded product image and one real uploaded package image through the public preview URL, each returning `200` with an image MIME type.
2. The exact rendered public product route containing `/previews/<slug>/uploads/product/...` in its DOM.
3. An exact rendered package-bearing public surface containing `/previews/<slug>/uploads/package/...`, not a placeholder.
4. Browser runtime errors classified separately from host Chromium warnings.

Do not report media fixed from the admin form preview, source diff, build, or direct origin response alone.

## Payment preview

State whether checkout uses a genuine provider sandbox invoice or an intentional local test finalizer. If a local finalizer is necessary, gate it narrowly to preview public path + test mode + absent provider secret; never enable it in production.

Public verification sequence:

1. Sign up/sign in with a cookie jar and verify session lookup.
2. Initiate checkout with a unique idempotency key.
3. Capture the purchase ID.
4. Confirm via the preview callback/webhook route.
5. Assert paid status and issued wallet benefits.
6. Repeat confirmation when idempotency is in scope.

## Build-base trap

Build with both exact values in one command:

```bash
VITE_BASE=/previews/<slug>/ \
VITE_API_BASE_URL=/previews/<slug>/api/v1 \
  npm run build
```

After publishing, inspect public HTML. Asset URLs must begin `/previews/<slug>/assets/`, not a production prefix. A successful default build can silently publish new HTML that still loads production assets.
