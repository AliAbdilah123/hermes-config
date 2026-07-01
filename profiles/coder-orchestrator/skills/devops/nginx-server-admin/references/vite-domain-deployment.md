# Vite Domain Deployment — Multi-Base-Path Pattern

When serving the same Vite SPA at both an IP path (`/projects/<slug>/`) and a domain root (`https://<domain>/`), you need two builds with different `base` paths. This reference covers the full workflow.

## Why Two Builds Are Needed

Vite bakes the `base` config and `VITE_API_URL` env var into the built HTML/JS at build time. A build with `base: "/projects/foo/"` produces `<script src="/projects/foo/assets/index-xxx.js">`. Serving this at a domain root (`/`) causes 404s for all assets because the browser requests `/projects/foo/assets/...` which doesn't exist at that path.

## Step-by-Step

### 1. Make vite.config.ts Base Configurable

```ts
// Before (hardcoded):
base: "/projects/<slug>/",

// After (configurable):
base: process.env.VITE_BASE || "/projects/<slug>/",
```

This is backward-compatible: existing builds without `VITE_BASE` still use the old path.

### 2. Check API URL Pattern

Look in the frontend's API client for how the base URL is constructed. Common pattern:

```ts
const DEFAULT_API_BASE = "/projects/<slug>"
// Falls back to this if VITE_API_URL is empty/unset
```

If the fallback is hardcoded, you MUST set `VITE_API_URL=/` explicitly (not empty string, which triggers the fallback).

### 3. Build for Domain Root

```bash
cd /home/ubuntu/<project>/apps/frontend
VITE_BASE=/ VITE_API_URL=/ VITE_API_BASE_URL=/ pnpm build --outDir /tmp/<slug>-domain-build --emptyOutDir
```

Notes:
- Process env vars override `.env.production` values in Vite.
- The `vite build` / `npx vite build` command may be flagged by the terminal tool as a potential server process. Use `background=true` with `notify_on_complete=true`, or use `pnpm build` which is less likely to be flagged.
- Verify the output: `grep -o 'src="[^"]*"' /tmp/<slug>-domain-build/index.html` — paths should start with `/assets/` not `/projects/<slug>/assets/`.

### 4. Deploy to Separate Directory

```bash
sudo mkdir -p /var/www/html/<slug>
sudo cp -r /tmp/<slug>-domain-build/* /var/www/html/<slug>/
sudo chown -R www-data:www-data /var/www/html/<slug>/
```

Keep the old build at `/var/www/html/projects/<slug>/` for the IP path — both coexist.

### 5. Create nginx Server Block for the Domain

Create `/etc/nginx/projects/<slug>-domain.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name <domain>;

    root /var/www/html/<slug>;
    index index.html;

    location ^~ /api/ {
        proxy_pass http://127.0.0.1:<backend-port>/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /media/ {
        proxy_pass http://127.0.0.1:<backend-port>/media/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 6. Test and Reload

```bash
sudo nginx -t && sudo systemctl reload nginx

# Test locally (simulates the domain via Host header)
curl -H "Host: <domain>" http://localhost/
curl -H "Host: <domain>" -o /dev/null -w "%{http_code}" http://localhost/

# Verify IP path still works
curl -o /dev/null -w "%{http_code}" http://localhost/projects/<slug>/
```

### 7. HTTPS (Once DNS + OCI Port 443 Are Ready)

```bash
# Verify DNS resolves
python3 -c "import socket; print(socket.gethostbyname('<domain>'))"

# Verify port 443 is reachable externally
curl -k --connect-timeout 5 https://168.110.213.104/health

# Run certbot — auto-configures 443 ssl + HTTP→HTTPS redirect
sudo certbot --nginx -d <domain>
```

## Backend CORS

Most project backends on this server use permissive CORS (echo Origin header or allow `*`). No backend changes are needed for a new domain. Verify by checking the backend's CORS middleware before assuming.

## Pitfalls

### Pitfall 1: Go Backend Redirect URLs Must Not Append projectPrefix for Domain Deployment

If the Go backend has a `frontendURL(path)` helper that constructs redirect URLs (OAuth callbacks, payment returns, etc.), it typically appends a hardcoded `projectPrefix` like `/projects/socialzen` to the base URL. This produces wrong redirects on the domain deployment.

**Bad** (from production bug):
```go
func (c appConfig) frontendURL(path string) string {
    base := nonempty(c.FrontendBaseURL, projectPrefix)
    // ❌ Always appends projectPrefix to absolute URLs
    if strings.HasPrefix(base, "http") && !strings.Contains(base, projectPrefix) {
        base = strings.TrimRight(base, "/") + projectPrefix
    }
    return base + path
}
```
→ Redirects to `https://domain.com/projects/socialzen/app/settings` but domain SPA is at root → white page.

**Good**:
```go
func (c appConfig) frontendURL(path string) string {
    base := nonempty(c.FrontendBaseURL, projectPrefix)
    // ✅ Custom domain → serve at root, no project prefix
    if strings.HasPrefix(base, "http") {
        base = strings.TrimRight(base, "/")
    }
    return base + "/" + strings.TrimLeft(path, "/")
}
```
→ `https://domain.com/app/settings` ✅

Also ensure the env uses the right variable name. This server's SocialZen project uses `firstEnv(default, "FRONTEND_BASE_URL", "FRONTEND_URL", "ALLOWED_ORIGIN")` — each can be set independently.

### Pitfall 2: Build Order Matters When Sharing `dist/`

If both deployments build into the same `dist/` directory (common with `pnpm build`), the **domain build must run first**, then the path-based build, or you'll overwrite the other deployment's assets with wrong paths.

Safe order:
```bash
# 1. Build domain (VITE_BASE=/)
VITE_BASE=/ pnpm build
sudo rsync -a dist/ /var/www/html/<slug>/

# 2. Build path-based (VITE_BASE=/projects/<slug>/)
VITE_BASE=/projects/<slug>/ pnpm build
sudo rsync -a dist/ /var/www/html/projects/<slug>/
```

The second build's output is correct for the second target because it overwrites the first. The reverse order (path-based first, then domain) deploys root-relative assets to both targets → path-based deployment breaks.

### Pitfall 3: OAuth Redirect URIs Must Match the Deployment

OAuth providers (Meta/Instagram, Google, etc.) validate the `redirect_uri` parameter. The redirect URI in `.env` must point to the correct backend callback URL for the deployment being used:
- Domain deployment: `https://domain.com/api/instagram/connect/callback`
- Path-based deployment: `https://ip/projects/socialzen/api/instagram/connect/callback`

If they mismatch, the OAuth flow either fails at the provider level or redirects to the wrong backend path.

### Pitfall 4: VITE_API_URL=/ Causes Double-Slash (`//api/...`) — normalizeApiBase Must Handle It

Setting `VITE_API_URL=/` for a domain root deployment causes the API base to be `"/"`. When the auth client or API client concatenates `${API_BASE}${path}` (e.g. `"/" + "/api/auth/get-session"`), the result is `"//api/auth/get-session"` — a **protocol-relative URL** that the browser resolves as `https://api/auth/get-session` (wrong domain → failed request).

**Fix**: in the frontend's `normalizeApiBase` (or equivalent), add a guard:

```ts
function normalizeApiBase(value: string | undefined): string {
  const trimmed = value?.trim()
  if (!trimmed) return DEFAULT_API_BASE  // unset → path-based default
  if (trimmed === "/") return ""          // ✅ domain root → empty base
  return trimmed.replace(/\/+$/, "")
}
```

With `API_BASE = ""`, the concatenation `"" + "/api/auth/get-session"` produces `"/api/auth/get-session"` — correct.

### Pitfall 5: `VITE_API_URL=` (Empty) in Bash Unsets the Variable

In bash, `VITE_API_URL= command` **unsets** the env var (it doesn't set it to empty string). Vite then falls back to `.env.production` which may have a stale value. Use an explicit value: `VITE_API_URL=/` for domain root, `VITE_API_URL=/projects/slug` for path-based.

### Pitfall 6: Monorepo Root Lacks `.env.production` — Env Vars from CLI are Required

When building from the monorepo root with `pnpm --filter frontend build`, Vite's `loadEnv` uses the CWD (monorepo root), which typically lacks `.env.production`. Environment values must be passed explicitly via CLI:

```bash
cd /home/ubuntu/project
VITE_BASE=/ VITE_API_URL=/ pnpm --filter frontend build  # domain
VITE_BASE=/projects/slug/ VITE_API_URL=/projects/slug pnpm --filter frontend build  # path-based
```

## Known Deployments Using This Pattern

| Project | Domain | IP Path | Backend Port |
|---------|--------|---------|-------------|
| SocialZen | socialzen.ahsanworks.com | /projects/socialzen/ | 8089 |

(Pending DNS + certbot as of 2026-06-30)
