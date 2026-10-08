# Root-domain SPA API URL construction

Use this when a deployed SPA renders but workspace/data loading fails with `Failed to construct 'URL': Invalid URL` while the API health endpoint is healthy.

## Failure pattern

An API helper constructs requests with an assumption that the document base is absolute:

```ts
new URL(`.${path}`, document.baseURI)
```

Root-domain rewrites or a relative `<base href="/">` can make the effective base `/`. URL construction then throws before `fetch`, so server logs and health probes can look normal.

## Reproduce before fixing

Add a boundary-level regression test that:

1. Sets `document.baseURI` to `/`.
2. Sets `location.origin` to the deployed origin.
3. Calls a real API-client method.
4. Asserts the resulting request origin and pathname.

Run it before the implementation change and require `Invalid URL`/`ERR_INVALID_URL`.

## Minimal fix

For intentionally root-relative same-origin API paths (`/api/...`), anchor them to an absolute origin:

```ts
const base = typeof location === 'undefined' ? 'http://localhost' : location.origin;
const url = new URL(path, base);
```

Keep the server/test fallback. Do not use this blindly for applications whose API is intentionally subpath-mounted; those need the canonical base-path helper.

## Deployment verification

- Run focused regression, full tests, type checks, and production build.
- Publish the built artifact, not only source.
- Verify public health and one real authenticated/data endpoint.
- Inspect the served hashed JS for the new origin-based logic.
- Exercise the post-login workspace in a browser when credentials are available. A `200` health response alone does not prove the user flow.
