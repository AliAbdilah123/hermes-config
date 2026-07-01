# Single Build + Sub_filter: Clean Domain Root URLs

## Problem

A Vite/React SPA is deployed at two URLs:
- Domain: `https://example.com/` (clean root URL, user-facing)
- IP path: `http://168.110.213.104/projects/example/` (secondary)

A single Vite build can only bake in ONE `base` path. Building with `VITE_BASE=/projects/example/` makes domain URLs show `/projects/example/` in the bar. Building with `VITE_BASE=/` breaks asset paths and routing on the IP path deployment.

## Solution

- **Build** with `VITE_BASE=/` — domain gets clean root URLs natively
- **Path-based deployment** uses nginx `sub_filter` to rewrite asset paths and inject runtime overrides (basename, API base)
- **One canonical build directory**: `/var/www/html/projects/<slug>/`

## Code Changes (one-time per project)

### 1. React Router basename — dynamic via `window.__BASENAME__`

In `main.tsx`, change:
```tsx
<BrowserRouter basename={import.meta.env.BASE_URL}>
```
to:
```tsx
const routerBasename =
  typeof window !== 'undefined' && (window as any).__BASENAME__
    ? (window as any).__BASENAME__
    : import.meta.env.BASE_URL;

// ...
<BrowserRouter basename={routerBasename}>
```

### 2. API base URL — dynamic via `window.__API_BASE__`

In the module that computes the API base URL (e.g. `lib/api.ts`, `lib/auth.ts`), add a `window.__API_BASE__` check as the highest-priority source:

```ts
function getBaseUrl(): string {
  if (typeof window !== 'undefined' && (window as any).__API_BASE__) {
    return (window as any).__API_BASE__ as string;
  }
  // ... existing fallback logic (VITE_API_BASE_URL env var, default)
}
```

## Nginx Config

### Domain Server Block (`/etc/nginx/projects/<slug>-domain.conf`)

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name <domain>;

    root /var/www/html/projects/<slug>;
    index index.html;

    # API & webhook at root level (build calls /api/...)
    location ^~ /api/ { proxy_pass http://127.0.0.1:<port>/api/; ... }
    location ^~ /webhooks/ { proxy_pass http://127.0.0.1:<port>/webhooks/; ... }

    # Also proxy path-prefixed URLs (DB may store full paths)
    location ^~ /projects/<slug>/api/ { proxy_pass http://127.0.0.1:<port>/api/; ... }
    location ^~ /projects/<slug>/webhooks/ { proxy_pass http://127.0.0.1:<port>/webhooks/; ... }

    location / {
        try_files $uri $uri/ /index.html;
    }

    # certbot-managed SSL...
}
```

### Path-Based Block in Default Server (`/etc/nginx/projects/default.conf`)

```nginx
location /projects/<slug>/ {
    alias /var/www/html/projects/<slug>/;
    index index.html;
    try_files $uri $uri/ /projects/<slug>/index.html;
    sub_filter_types text/html;
    sub_filter 'src="/assets/' 'src="/projects/<slug>/assets/';
    sub_filter 'href="/assets/' 'href="/projects/<slug>/assets/';
    sub_filter '</head>' '<script>window.__BASENAME__="/projects/<slug>";window.__API_BASE__="/projects/<slug>/api/v1"</script></head>';
    sub_filter_once off;
}
```

### API base values per project

| Project | `__API_BASE__` value for path-based | Reason |
|---------|-------------------------------------|--------|
| komuna | `/projects/komuna/api/v1` | Default API base is `${BASE_URL}api/v1` |
| socialzen | `/projects/socialzen` | Code appends `/api` to the base separately |
| boilerplate | `/projects/boilerplate/api/v1` | Default pattern |

Inspect the project's API client to determine the correct value.

## Build & Deploy

```bash
cd <project>/apps/web
rm -rf dist
VITE_BASE=/ VITE_API_BASE_URL=/api/v1 npm run build
# For pnpm projects: VITE_BASE=/ VITE_API_URL=/ pnpm build

sudo rsync -a --delete dist/ /var/www/html/projects/<slug>/
sudo nginx -t && sudo systemctl reload nginx
```

## Verification

```bash
# Domain: clean root, no redirect, assets at /assets/...
curl -k https://<domain>/                           # → 200
curl -k https://<domain>/some-deep-route             # → 200 (SPA fallback)

# IP path: assets rewritten to /projects/<slug>/assets/...
curl http://168.110.213.104/projects/<slug>/         # → 200

# Verify asset rewriting on IP path
curl -s http://168.110.213.104/projects/<slug>/ | grep -o 'src="[^"]*"' | head -5
# Should show: src="/projects/<slug>/assets/index-XXXXX.js"
# NOT: src="/assets/index-XXXXX.js"

# Verify runtime overrides injected on IP path
curl -s http://168.110.213.104/projects/<slug>/ | grep -o '__BASENAME__[^<]*'
# Should show: __BASENAME__="/projects/<slug>"
```

## Pitfalls

- **Domain must NOT redirect** to `/projects/<slug>/`. The user wants clean root URLs.
- **`sub_filter_once off` is mandatory** — without it, only the first asset reference is rewritten.
- **API base value must match** what the path-based nginx config proxies. Double-check the project's API client default.
- **Committed HTML changes** apply to the source. After deploying, verify with `md5sum` that the deployed `index.html` matches `dist/index.html`.
- **HTML-only sub_filter**: `sub_filter_types text/html;` is sufficient for Vite builds — CSS and JS use relative URLs internally. If a project inlines assets unusually, extend to `text/css application/javascript`.
- **Duplicate MIME warning**: `sub_filter_types text/html;` in multiple location blocks produces a harmless `duplicate MIME type "text/html"` warning. Safe to ignore.
