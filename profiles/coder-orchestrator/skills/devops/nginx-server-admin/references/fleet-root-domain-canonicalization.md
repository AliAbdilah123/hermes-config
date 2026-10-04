# Fleet Root-Domain Canonicalization

Use when migrating many nginx applications from shared `/projects/<slug>/` URLs to one hostname per application while retaining one deployed build.

## Canonical policy used here

- Default browser URL: `https://dev-<slug>.ahsanworks.com/`.
- Explicit exceptions keep their assigned hostname but still mount at `/`.
- Browser-visible URLs must not require `/projects/<slug>/`.
- Preview, PRD, system, disabled/retired, and API-only routes are not browser projects and must be classified rather than assigned invented frontends.
- Keep legacy path routes as compatibility endpoints until stored URLs and external callbacks are proven migrated.

## Safe sequence

1. Inventory effective `nginx -T`: `server_name`, browser locations, roots/aliases, upstreams, previews, API-only routes, and disabled routes.
2. Confirm wildcard DNS with two public resolvers. A wildcard record is typically entered as name `*`, not `*.example.com`.
3. Classify applications by delivery type:
   - Native domain-root vhost: add the canonical hostname to that existing vhost so uploads, API rules, headers, and deep links remain intact.
   - Static/path-mounted SPA: root-mount its deployment and rewrite generated mount prefixes in HTML and JavaScript.
   - Prefix-mounted upstream: proxy root requests to the existing prefix while preserving URI suffixes.
   - Broken or API-only upstream: do not publish it as a browser project merely because an nginx route exists.
4. Run `nginx -t` before every reload. A failed test means do not reload.
5. Verify origin first, then both public Cloudflare edge addresses with cache-busting query strings.
6. Only after canonical public verification, redirect superseded standalone domains to the canonical root. Preserve query/path only if explicitly required and tested.

## Generic prefix bridge

A variable-bearing `proxy_pass http://127.0.0.1/projects/$slug/;` can produce incorrect URI behavior: root HTML may work while `/assets/*.js` falls through to SPA HTML. Prefer an explicit rewrite followed by a variable-free upstream:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name ~^dev-(?<project_slug>app-one|app-two)\.example\.com$;

    location / {
        rewrite ^/(.*)$ /projects/$project_slug/$1 break;
        proxy_pass http://127.0.0.1;
        proxy_set_header Host dev.example.com;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cookie_path ~^/projects/[^/]+/? /;

        sub_filter_types text/html application/javascript text/javascript text/css application/json;
        sub_filter '"/projects/$project_slug/' '"/';
        sub_filter "'/projects/$project_slug/" "'/";
        sub_filter '`/projects/$project_slug/' '`/';
        sub_filter_once off;
    }
}
```

Use a regex `server_name` or regex map when a long hostname list exceeds nginx `server_names_hash_bucket_size` or `map_hash_bucket_size`; avoid global hash tuning when a smaller config expresses the same allowlist.

## Verification invariant

A root `200 text/html` is insufficient. For every canonical hostname require:

1. `https://host/` returns expected app HTML and final URL remains under that hostname with no `/projects/` mount prefix.
2. Parse the first referenced JS/CSS asset and request it publicly. Require `200` and the correct JavaScript/CSS MIME type. `200 text/html` is an SPA fallback failure.
3. Inspect served HTML and relevant compiled JS for the old mount prefix. Distinguish route/API/base prefixes from harmless strings such as source-map paths, application entities named `projects`, or stored compatibility links.
4. Probe a known application-specific API/health endpoint. A service-level `404` may be legitimate if that route does not exist; ensure it is not HTML fallback and use an actual known endpoint where possible.
5. Verify deep-link SPA fallback, cookies, uploads/media, callbacks/webhooks, and any lazy-loaded chunks for applications that use them.
6. Confirm `nginx -t`, active service state, and public HTTPS on each edge.

## Cloudflare boundary

If origin `Host:` requests show the new redirect/content but public requests never appear in nginx access logs and return unrelated content, a Cloudflare hostname-specific Worker, redirect rule, tunnel, or alternate origin is intercepting the hostname. Do not claim nginx changed that legacy hostname. Report the canonical hostname as working and require the Cloudflare rule/origin to be updated separately.

Cloudflare can cache an earlier bad asset response. Verify origin separately and use a new query string when checking the edge. Do not treat cache-busting as a substitute for fixing routing.
