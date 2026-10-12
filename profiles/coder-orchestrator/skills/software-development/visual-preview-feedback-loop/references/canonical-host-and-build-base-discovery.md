# Canonical host and build-base discovery

Use before building or publishing an existing SPA when both a legacy shared subpath and a root-mounted project domain may exist.

## Why

A repository may still document or test a historical `/projects/<slug>/` URL while active routing exposes the product at `https://dev-<slug>.<domain>/`. Building with the old subpath can deploy successfully but emit unusable asset URLs on the canonical host. Conversely, probing only the legacy public URL can produce a 404 even though the deployment is healthy.

## Procedure

1. Inspect active routing configuration, not only repository docs or backup configs.
2. Identify independently: filesystem publication directory, internal compatibility route, and externally canonical host/mount.
3. Build for the canonical public mount (`/` for root-mounted hosts; exact trailing-slash prefix for nested mounts).
4. Publish output and restart only services actually changed or required by project workflow.
5. Fetch canonical HTML with a fresh cache-buster and extract every entry JS/CSS URL.
6. Require those exact assets to return successfully with correct MIME types.
7. Run E2E with its base URL explicitly set to the discovered canonical host; do not let an obsolete default silently test a legacy route.
8. Keep deployment proof separate from interaction proof.

## Diagnostic rule

If service health passes but public HTML returns 404, stop retrying the service and re-check virtual-host routing. If HTML loads but the app is blank, compare emitted asset prefixes to the public mount before changing application code.

## Build examples

```sh
# Root-mounted project domain
npm run build -- --base=/

# Nested shared route
npm run build -- --base=/projects/example/
```

The active route decides; historical conventions do not.
