---
name: nginx-server-admin
description: Administer the nginx web server on the user's Oracle Cloud instance — SSL/HTTPS setup, port and firewall management (two-layer ufw + OCI Security List), project routing config, and deployment verification. Use when the user asks to enable HTTPS, open ports, configure SSL certs, add or modify nginx routes, or troubleshoot public access issues.
---

# Nginx Server Admin

Administer nginx and network access on the user's Oracle Cloud instance (IP `168.110.213.104`).

## Server Layout

- **nginx config**: `/etc/nginx/nginx.conf` includes `/etc/nginx/projects/*.conf`
- **Active project config**: `/etc/nginx/projects/default.conf` — single `server` block with path-based routing under `/projects/<slug>/`
- **Static project files**: `/var/www/html/projects/<slug>/`
- **PRD/review HTML files**: `/usr/share/nginx/html/prds/` (served at `/prd/<name>`)
- **Project API backends**: each project's Go/Node API runs on a localhost port (e.g. socialzen=8089, komuna=8095, self-flow=8096), proxied via `location ^~ /projects/<slug>/api/`
- **SSL certs**: `/etc/nginx/ssl/selfsigned.crt` + `.key` (self-signed, 365-day expiry)

## Oracle Cloud Two-Layer Firewall (critical)

This server has **two independent firewalls**. Both must allow a port for public access:

1. **OS-level (ufw)** — `sudo ufw allow <port>/tcp`. You manage this from the terminal.
2. **Network-level (OCI Security List)** — configured in the Oracle Cloud Console, NOT from the server. See `references/oracle-cloud-security-list.md` for exact steps.

**Diagnostic pattern**: If `curl http://localhost:<port>/` works but `curl http://168.110.213.104:<port>/` times out (not "connection refused", but hangs), the OCI Security List is blocking the port. ufw is open but the network firewall is not.

Port 80 was pre-opened in both layers. New ports (e.g. 443) need both.

## Enabling HTTPS

### Self-Signed Cert (bare IP, no domain)

Use when the user has no domain name and accepts browser warnings.

```bash
# 1. Generate cert (include IP as SAN)
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/CN=168.110.213.104" \
  -addext "subjectAltName=IP:168.110.213.104"

# 2. Add listen 443 ssl to the server block in /etc/nginx/projects/default.conf
#    Add these lines after the existing listen 80 directives:
#    listen 443 ssl;
#    listen [::]:443 ssl;
#    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
#    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
# Use sudo perl -0777 -i -pe for multiline edits (patch tool refuses system paths)

# 3. Open ufw
sudo ufw allow 443/tcp

# 4. Test and reload
sudo nginx -t && sudo systemctl reload nginx

# 5. Verify locally (bypasses OCI firewall)
curl -k https://localhost/health
curl -k -o /dev/null -w "%{http_code}" https://localhost/projects/socialzen/
```

After server-side setup, the user must open port 443 in the OCI Security List (see `references/oracle-cloud-security-list.md`).

### Let's Encrypt (requires a domain)

Use when the user has a domain pointed at `168.110.213.104`. Free, auto-renewing, no browser warnings.

**Prerequisites** (all three must be true before running certbot):
1. DNS A record for the domain resolves to `168.110.213.104` — verify: `python3 -c "import socket; print(socket.gethostbyname('<domain>'))"`
2. OCI Security List has port 443 open (see `references/oracle-cloud-security-list.md`)
3. nginx server block for the domain exists and is loaded (certbot will modify it)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d <domain>
# Certbot auto-edits the nginx server block: adds listen 443 ssl, cert paths, and HTTP→HTTPS redirect
# Renewal timer is set up automatically via systemd
```

Let's Encrypt cannot issue certs for bare IP addresses — a domain is required.

## Domain Integration for Path-Based Projects (Single Build, Clean Root URL)

When a user wants a custom domain for a path-based Vite/React project, use a **single build** with `VITE_BASE=/` plus nginx `sub_filter` on the path-based deployment. The domain gets clean root URLs, the IP path continues to work — **one canonical build directory** (`/var/www/html/projects/<slug>/`).

```
https://<domain>/          → root /var/www/html/projects/<slug>/   (native, no sub_filter)
http://<ip>/projects/<slug>/ → alias + sub_filter rewrites assets  (injects runtime overrides)
```

This avoids maintaining two separate build directories and two separate Vite builds. Clean domain URLs without redirect.

### Code Prerequisites (one-time per project)

The frontend must support runtime overrides for React Router `basename` and API base URL. See `references/single-build-subfilter.md` for the exact code patches.

### Setting Up the Domain Config

```nginx
# /etc/nginx/projects/<slug>-domain.conf
server {
    listen 80;
    listen [::]:80;
    server_name <domain>;

    root /var/www/html/projects/<slug>;          # ← canonical build dir
    index index.html;

    # API/webhook proxied at root level AND path-prefixed (DB may store both)
    location ^~ /api/ { proxy_pass http://127.0.0.1:<port>/api/; ... }
    location ^~ /projects/<slug>/api/ { proxy_pass http://127.0.0.1:<port>/api/; ... }

    location / {
        try_files $uri $uri/ /index.html;
    }

    listen 443 ssl; ... # certbot
}
```

### Setting Up the Path-Based Config (sub_filter)

The path-based deployment in `/etc/nginx/projects/default.conf` must rewrite asset paths and inject runtime overrides:

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

`sub_filter` requires `ngx_http_sub_module` — included by default in Ubuntu's nginx. Verify: `sudo nginx -V 2>&1 | grep sub_module`.

### Deploy

```bash
# Build with root base
cd <project>/apps/web
rm -rf dist
VITE_BASE=/ VITE_API_BASE_URL=/api/v1 npm run build   # (or pnpm build for pnpm projects)

# Deploy to canonical directory (updates BOTH domain and IP path)
sudo rsync -a --delete dist/ /var/www/html/projects/<slug>/

# Reload
sudo nginx -t && sudo systemctl reload nginx
```

### Verify

```bash
# Domain: clean root URL, no redirect, assets at /assets/...
curl -k https://<domain>/
curl -k https://<domain>/some-deep-route   # SPA fallback works

# IP path: assets rewritten to /projects/<slug>/assets/..., overrides injected
curl http://168.110.213.104/projects/<slug>/

# Both should return 200 with correct asset hashes
```

### Cleanup Old Duplicate Directory

```bash
sudo rm -rf /var/www/html/<slug>   # if an old domain-specific build dir exists
```

⚠️ **Pitfalls for this approach:**
- The frontend MUST support `window.__BASENAME__` and `window.__API_BASE__` runtime overrides. Without these code changes, the path-based deployment will have broken routing and API calls. See `references/single-build-subfilter.md`.
- `sub_filter_once off` is critical — without it, only the first match in the HTML is rewritten, leaving other asset references broken.
- The API base value injected via `__API_BASE__` must match what the path-based nginx config proxies. For komuna: `/projects/komuna/api/v1`. For socialzen: `/projects/socialzen` (its code appends `/api` separately).
- The `location ^~ /api/` block on the domain server block is for the domain deployment (root build calls `/api/...`). The path-based deployment injects `__API_BASE__` so it calls the correct path-prefixed URL.
- `sub_filter_types text/html` may produce a harmless warning about duplicate MIME types if multiple projects use it — this is safe to ignore.
- Never redirect the domain root to `/projects/<slug>/`. The user wants clean URLs.

## Adding a New Project Route

To serve a new project under `/projects/<slug>/`:

1. Build the frontend, copy to `/var/www/html/projects/<slug>/`
2. Add a `location` block to `/etc/nginx/projects/default.conf`:
   ```nginx
   location = /projects/<slug> { return 301 /projects/<slug>/; }
   location /projects/<slug>/ {
       alias /var/www/html/projects/<slug>/;
       index index.html;
       try_files $uri $uri/ /projects/<slug>/index.html;
   }
   ```
3. If the project has an API, add a proxy block:
   ```nginx
   location ^~ /projects/<slug>/api/ {
       proxy_pass http://127.0.0.1:<port>/api/;
       proxy_http_version 1.1;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```
4. `sudo nginx -t && sudo systemctl reload nginx`
5. Verify: `curl -o /dev/null -w "%{http_code}" http://localhost/projects/<slug>/`

## Editing System nginx Configs

The `patch` tool refuses to write to `/etc/nginx/`. Use terminal with `sudo`:
- Single-line edits: `sudo sed -i 's/old/new/' /etc/nginx/projects/default.conf`
- Multiline edits: `sudo perl -0777 -i -pe 's/old/new/' /etc/nginx/projects/default.conf`
- Always back up first: `sudo cp /etc/nginx/projects/default.conf /etc/nginx/projects/default.conf.bak.$(date +%Y%m%d%H%M%S)`

## Pitfalls

- **Dist not auto-deployed to nginx**: After `npm run build` / `npx vite build` completes, the build output sits in the project's local `dist/` directory. There is no CI/CD auto-deploy. You MUST manually copy it to the nginx-served directory: `cp -r dist/* /var/www/html/projects/<slug>/`. If the user says they "don't see" a change you know you made, check `md5sum` of the deployed `index.html` against the built `dist/index.html` — stale deployment is the #1 suspect.
- **Domain deploys use the same directory now**: Domains are served from `/var/www/html/projects/<slug>/` via the single-build + sub_filter pattern. Deploying to that one directory updates BOTH the IP path and the domain. If a domain existed before this change, it may have had a stale `/var/www/html/<slug>/` copy — remove it. The #1 stale-domain suspect is an out-of-date `/var/www/html/projects/<slug>/` — check `md5sum` against the source `dist/index.html`.
- **Single canonical build directory**: All deploys go to `/var/www/html/projects/<slug>/` — this is the ONLY build directory for the project. Both the domain and the IP path serve from here. If you find a `/var/www/html/<slug>/` directory (without `projects/`), it is a stale duplicate from an old dual-build setup — remove it after confirming the new single-build config is active.
- **Forgetting the OCI Security List**: Opening ufw alone is not enough. If public access times out but localhost works, the Security List is the blocker — you cannot fix it from the terminal.
- **Self-signed cert browser warnings**: Browsers show "Not Secure" / "Your connection is not private". Users must click Advanced then Proceed. This is expected, not a bug. Mention the upgrade path to Let's Encrypt if they get a domain.
- **Cert expiry**: Self-signed certs expire. Regenerate with the same openssl command or set up a calendar reminder. Let's Encrypt auto-renews via systemd timer.
- **nginx config syntax**: Always run `sudo nginx -t` before reload. A syntax error in the config will prevent nginx from starting on reload.
- **Vite base path mismatch**: If a Vite SPA built with `base: "/projects/foo/"` is served at a different path (e.g. domain root `/`), all asset requests 404 because the built HTML references `/projects/foo/assets/...`. You must rebuild with the correct `base` for each deployment path. See "Domain Integration for Path-Based Projects" above.
- **Domain config missing path-prefixed media/api blocks**: When a project migrates from path-based (`/projects/<slug>/`) to a custom domain, the domain nginx config typically adds `location ^~ /api/` and `location ^~ /media/`. But URLs stored in the database (e.g. media paths from `SaveUpload`) still use the FULL prefix `/projects/<slug>/media/user_.../upload_...jpg`. If the domain config does NOT also proxy `location ^~ /projects/<slug>/media/` and `location ^~ /projects/<slug>/api/`, those URLs fall through to the SPA catch-all (`location /`) and return HTML instead of the actual image. External platforms (Instagram/Facebook Graph API) silently receive HTML, causing publish failures with no visible error. Always add BOTH the root-level and path-prefixed location blocks to the domain config. Verify with `curl -sI https://<domain>/projects/<slug>/media/<test-file>` returning `Content-Type: image/jpeg` — not `text/html`. **Follow-on**: even after fixing the nginx config, Cloudflare may have cached the old HTML fallback (200 OK with wrong content-type) for hours. See `references/cloudflare-stale-cache-nginx-routing.md` for diagnosis and cache-busting fix.
- **Vite env var precedence**: Process env vars (e.g. `VITE_API_URL=/ vite build`) override `.env.production` values. Use this to build the same source for different deployment targets without modifying env files.
- **Missing `.env` file causes blank page on rebuild**: If a project's `.env.example` contains `VITE_BASE_PATH=/projects/<slug>/` but no corresponding `.env` file exists, the Vite build silently defaults to `base: "/"`. All asset references in `index.html` become root-relative (`/assets/...`) instead of path-prefixed (`/projects/<slug>/assets/...`). The page renders blank with no visible errors — the HTML loads but every JS/CSS request 404s. **Fix**: verify `ls packages/*/.*env packages/*/.env` after a rebuild produces a blank page — the `.env` file is the #1 suspect. Create it at `packages/<fe>/env` with `VITE_BASE_PATH=/projects/<slug>/` matching the `.env.example` value.
- **Backend redirect URLs for dual deployment**: When the backend constructs redirect URLs (OAuth callbacks, payment returns), it must use the correct base for each deployment. A common bug: the backend's `frontendURL()` helper appends a hardcoded project prefix even when the domain SPA is served at root. See `references/vite-domain-deployment.md` Pitfalls 1–3 for the full pattern.
- **Cloudflare proxied DNS + certbot redirect loop**: If `curl -L https://<domain>/` stays at `301 Location: https://<same-domain>/`, Cloudflare may be hitting origin HTTP while certbot's HTTP block redirects to HTTPS. Serve the app on both HTTP and HTTPS in the main domain server block and remove the redirect-only HTTP block; see `references/vite-domain-deployment.md` HTTPS section.
- **Domain config blank page (missing reverse sub_filter)**: If the build was deployed with a non-root base (e.g. `/projects/<slug>/assets/...`), the domain config needs reverse `sub_filter` to STRIP the path prefix, otherwise assets 404 → blank page. Add to the domain's `location /` block:
  ```nginx
  sub_filter 'src="/projects/<slug>/assets/' 'src="/assets/';
  sub_filter 'href="/projects/<slug>/assets/' 'href="/assets/';
  sub_filter '</head>' '<script>window.__BASENAME__="/";window.__API_BASE__="/api/v1"</script></head>';
  sub_filter_once off;
  ```
  The preferred fix is rebuilding with `VITE_BASE=/` so no sub_filter is needed on the domain side — only on the path-based deployment. But when you can't rebuild (hotfix, shared build directory), the reverse sub_filter works.

## References

- See `references/oracle-cloud-security-list.md` for step-by-step instructions to open a port in the OCI Security List (the network-level firewall that cannot be configured from the server).
- See `references/single-build-subfilter.md` for the full code patches, nginx sub_filter config, and verification steps for the single-build domain + path deployment pattern (the current preferred approach).
- See `references/vite-domain-deployment.md` for the legacy dual-build pattern (historical reference only — do NOT use for new setups).
- See `references/cloudflare-stale-cache-nginx-routing.md` for diagnosing and fixing stale Cloudflare cache after nginx routing changes (HTML cached as images, wrong content-type).
