# Domain Config for Existing Path-Based Build (No Rebuild)

When a project is already built with a path-prefixed base (e.g. `/projects/self-flow/`) and a new domain needs to serve it **without rebuilding**:

## Full Domain Config Template

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name <domain>;

    root /var/www/html/projects/<slug>;
    index index.html;

    # Root-level API proxy (domain clients call /api/...)
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:<port>/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Path-prefixed API proxy (DB-stored URLs use /projects/<slug>/api/...)
    location ^~ /projects/<slug>/api/ {
        proxy_pass http://127.0.0.1:<port>/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /projects/<slug>;
    }

    location / {
        try_files $uri $uri/ /index.html;
        # Rewrite path-prefixed strings to root in HTML and JS
        sub_filter_types text/html application/javascript text/javascript;
        sub_filter '"/projects/<slug>/' '"/';
        sub_filter "'/projects/<slug>/" "'/";
        sub_filter 'basename:"/projects/<slug>/"' 'basename:"/"';
        sub_filter_once off;
    }
}
```

## Key Points

- **`sub_filter_types application/javascript` is required** — React Router `basename` and other paths are in `.js` bundles, not `.html`
- **Both quote styles** (`"` and `'`) needed — JS bundles use both
- **No redirect** from domain root to `/projects/<slug>/` — user wants clean URLs

## Verification

```bash
# 1. Domain root returns the app (not "hello" from default server)
curl -sI https://<domain>/ | grep -i content-type
# Content-Type: text/html

# 2. JS bundle has basename rewritten to root
curl -s https://<domain>/assets/index-<hash>.js | grep -o 'basename:"[^"]*"'
# basename:"/"

# 3. No leftover path-prefixed strings in JS
curl -s https://<domain>/assets/index-<hash>.js | grep -c '/projects/<slug>'
# 0

# 4. IP path still works unchanged
curl -sI http://168.110.213.104/projects/<slug>/ | grep -i content-type
# Content-Type: text/html
```

## Real Example (self-flow)

Build has `base: "/projects/self-flow/"` with React Router `basename:"/projects/self-flow/"` hardcoded.
Domain `selfflow.ahsanworks.com` uses config above at `/etc/nginx/projects/self-flow-domain.conf`.
Single build dir `/var/www/html/projects/self-flow/` serves BOTH domain and IP path.
