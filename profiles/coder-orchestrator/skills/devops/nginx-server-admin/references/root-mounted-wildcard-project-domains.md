# Root-Mounted Wildcard Project Domains

Use when migrating many path-mounted apps from `https://host/projects/<slug>/` to one hostname per app, such as `https://dev-<slug>.example.com/`, while preserving existing builds.

## Required sequence

1. Confirm wildcard DNS using at least two public resolvers. Local resolver results may retain an earlier negative answer.
2. Confirm the edge certificate covers `*.example.com` before changing nginx.
3. Inventory each route from `nginx -T`; classify static SPA, reverse-proxied app, API-only app, preview/system route, or retired route.
4. Migrate and verify one representative app first.
5. Keep the browser URL at `/`. Do not redirect the new root to `/projects/<slug>/`.
6. Verify each app independently before retiring its old URL. A generic fleet proxy is only a candidate baseline, not proof all apps share the same routing semantics.

## Existing path-based static build

A dedicated domain vhost can serve the existing leaf and rewrite compiled prefixes:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name dev-<slug>.example.com;
    root /var/www/html/projects/<slug>;
    index index.html;

    location ^~ /api/ {
        proxy_pass http://127.0.0.1:<port>/api/;
        # standard forwarding headers
    }

    location / {
        try_files $uri $uri/ /index.html;
        sub_filter_types text/html application/javascript text/javascript text/css application/json;
        sub_filter '"/projects/<slug>/' '"/';
        sub_filter "'/projects/<slug>/" "'/";
        sub_filter '`/projects/<slug>/' '`/';
        sub_filter '"/projects/<slug>"' '""';
        sub_filter "'/projects/<slug>'" "''";
        sub_filter '`/projects/<slug>`' '``';
        sub_filter_once off;
    }
}
```

Use `location /`, not `location = /`, when `try_files ... /index.html` internally redirects: an exact-root filter may be bypassed by the internal index request, leaving legacy asset paths in returned HTML.

## Fleet compatibility proxy

A regex `server_name` can avoid nginx name-hash pressure from a long hostname list:

```nginx
server_name ~^dev-(?<project_slug>app-one|app-two)\.example\.com$;
```

A shared proxy may internally map `/` to `/projects/$project_slug/`, but do not assume it works for:

- services that natively mount only `/`;
- upstreams whose prefix route strips or preserves the path differently;
- static routes that fall through to a generic `/projects/` alias;
- apps with distinct API prefixes, WebSockets, cookies, uploads, media, or auth callbacks.

Probe all hosts and split exceptions into dedicated vhosts.

## Validation

For every hostname verify:

- root returns the expected app fingerprint/title, not merely HTTP 200;
- final browser URL contains no `/projects/...`;
- HTML references root assets such as `/assets/...`;
- referenced JS/CSS returns the correct MIME type;
- served JavaScript contains zero legacy prefix occurrences;
- API health/auth boundary reaches the correct backend;
- cookies have a root-compatible path;
- deep links fall back correctly;
- both Cloudflare edge IPs work when proxied;
- old hostname/path is retired or redirected only after the replacement passes.

Add a cache-busting query while inspecting transformed HTML/JS through Cloudflare. Compare origin-host output with edge output: if origin has zero legacy strings but edge still has them, treat it as cache, not nginx failure.

## DNS propagation diagnosis

After creating a wildcard record, public resolvers may return an answer while a local resolver still caches `NXDOMAIN`. Query Cloudflare and Google DoH directly, then use `curl --resolve <host>:443:<edge-ip>` to test public edge TLS and routing without relying on local DNS. Do not report the hostname inaccessible solely from the local resolver once authoritative/public resolvers answer.
