# Komuna Prototype Deployment Notes

Host: `dev.ahsanworks.com`
Nginx prefix: `/projects/komuna/`
Static alias: `/var/www/html/projects/komuna/`
API proxy: `http://127.0.0.1:8095/api/` forwarded as `/projects/komuna/api/`

## Sub_filter Rules

All HTML responses under `/projects/komuna/` rewrite asset and API paths:

- `src=\"/assets/` → `src=\"/projects/komuna/assets/`
- `href=\"/assets/` → `href=\"/projects/komuna/assets/"`
- inject before `</head>`:
  - `window.__BASENAME__=\"/projects/komuna\";`
  - `window.__API_BASE__=\"/projects/komuna/api/v1\"`

Effect: never place raw `/assets/` references in manually written HTML
inside prototypes; always build via Vite so chunk filenames are hash-based.

## Canonical Sequence

```bash
cd /home/ubuntu/projects/komuna/apps/web
npm run build
sudo rm -rf /var/www/html/projects/komuna/*
sudo cp -r dist/* /var/www/html/projects/komuna/
sudo chown -R www-data:www-data /var/www/html/projects/komuna/
curl -I http://dev.ahsanworks.com/projects/komuna/<route>
```

## Verification Patterns

- Header check: expect `HTTP/1.1 200 OK`.
- Remote HTML snapshot is unreliable from this environment because
  browser automation may lack Chromium; use `curl` and bundle grep.
- Bundle grep: inspect `/var/www/html/projects/komuna/assets/index-*.js`
  for prototype string literals as evidence of inclusion.
- Always provide the user with the `/projects/komuna/<route>` path,
  avoiding the root `/` which requires an auth token in this setup.

## Common Mistakes

- Partial copy keeping old `index.html` after rename.
- Hardcoding `__BASENAME__` in prototypes instead of relying on build.
- Using `User=` or `Group=` in user-level systemd units: failure mode is
  `status=216/GROUP`.
- Treating browser snapshot unavailability as a hard blocker for
  deployment; the acceptance criterion is 200 + bundle evidence here.
