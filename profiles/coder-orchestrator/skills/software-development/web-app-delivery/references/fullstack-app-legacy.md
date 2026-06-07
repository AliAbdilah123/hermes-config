# Legacy skill package: `fullstack-app`

This file preserves the former `fullstack-app` SKILL.md after consolidation into `web-app-delivery`. Relative support-file links have been rewritten to the re-homed files under `web-app-delivery`.

---

---
name: fullstack-app
description: >
  Build and serve a full-stack app with React+TS frontend and Go backend,
  plus SQLite storage, exposed via nginx on `<publicIP>/projects/<projectName>`.
  Trigger: user asks to build a project with unspecified/unset default stack,
  scaffolds full-stack project, serve publicly, or generate public link after deployment.
category: software-development
---

# 🏗️ Fullstack App: React + TypeScript + Go + SQLite

The user’s default deliverable shape unless overridden:

- **Frontend:** TypeScript + React built app
- **Backend:** Go, APIs under `/api/v1/*`
- **Database:** SQLite

## Constraints
- Once the user confirms the stack choices, keep them for the rest of the task; do not silently change the stack mid-build.
- Required output is a working public link, not a build log.

## Recommended sequence

### 1. Frontend scaffold

Use Vite + React + TypeScript template.

Configure `vite.config.ts`:

```ts
export default defineConfig({
  base: `/projects/<projectName>/`,
  plugins: [react()],
})
```

> Without `base`, asset URLs in the built HTML will be `/assets/...`, breaking serving under `/projects/<projectName>/`.

- Keep imports clean to satisfy TypeScript.
- After editing `src/App.tsx`, run `npm run build` and verify the `dist/` folder contains:
  - `index.html`
  - `assets/` directory (JS/CSS)

### 2. Backend scaffold

`main.go` minimal pattern:

- Open SQLite DB at `backend/data.db`
- Create a `visits` table if not exists (or whatever schema the task needs)
- Register Go HTTP handlers under `/api/v1/...`
- Serve static files from `frontend/dist/` via `http.FileServer(http.Dir(...))`
- Make sure non-prefixed paths return `index.html` (SPA fallback)

### 3. Run + verify backend

```bash
go build -o server ./...
./server &   # or start as proper background process
curl http://127.0.0.1:8080/api/v1/<endpoint>
```

### 4. Nginx reverse proxy for public serving

Append or update a server block:

```nginx
server {
  listen 80;
  server_name _;

  location /projects/<projectName>/ {
    alias /path/to/project/frontend/dist/;
    index index.html;
    try_files $uri $uri/ /projects/<projectName>/index.html;
  }

  location /api/v1/ {
    proxy_pass http://127.0.0.1:8080/api/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

### 5. Reload nginx

**Always verify:**

```bash
sudo nginx -t
sudo kill -HUP $(pgrep -x nginx | head -1) && sudo nginx -s reload
# or: sudo systemctl reload nginx
```

### 6. Tail validation

Test from the server itself:

```bash
curl -I http://127.0.0.1/projects/<projectName>/
curl -s  http://127.0.0.1/api/v1/<endpoint>
```

Also run a visual smoke check after deploying the built frontend. A successful `curl`/build does not catch layout regressions such as hero/header overlap, clipped navigation, or unreadable text. Capture a screenshot with a headless browser, inspect it, fix obvious visual issues, rebuild, redeploy, and re-check before reporting done.

See `references/fullstack-app-visual-smoke-checks.md` for a compact example from a completed app session.

If those checks pass, the public path works.

### 7. Production-grade refinement pass

When the user asks to refine an existing app until it is production grade, do a real hardening pass rather than only polishing UI:

- Add backend tests, JSON error envelopes, strict method handling, request size limits, security headers, server timeouts, readiness checks, configurable env, and protected mutation/admin endpoints.
- Move SQLite runtime state out of the repo, enable WAL/busy timeout, and use transactions for mutations.
- Add frontend loading/error/empty states, disabled pending actions, token/auth UI when relevant, and accessibility/focus polish.
- Deploy via systemd + nginx, verify localhost-only backend binding, and keep secrets out of chat.
- Add or update a deployment runbook.
- If the user's workflow expects dashboard visibility, mirror the work into Hermes Kanban even when coding proceeds via autonomous local branches/commits.

See `references/fullstack-app-production-hardening.md` for the compact checklist.

## Pitfalls and workarounds

### Path substitution with `go:embed`

`embed.FS` does not follow symlinks. Copy the contents of `frontend/dist/` into a real directory (e.g., `frontend-public/`) before embedding, or skip `embed` entirely and use `http.Dir("frontend/dist")`. The simpler pattern is to use `http.Dir` rather than `//go:embed` for the React build.

### `proxy_pass` rewrites

When `proxy_pass http://upstream/api/v1/` is used, nginx strips the matching prefix and forwards `/api/v1/foo` to the backend as `/foo`. Either:

- Append a trailing slash: `proxy_pass http://127.0.0.1:8080/api/v1/;`
- Or use `proxy_pass http://127.0.0.1:8080;` and let the full `/api/v1/...` path reach backend

### `alias` vs `root`

`location /projects/<name>/` with `alias /path/;` serves files under `/path/`. Do **not** append the trailing `$uri` again (e.g., `alias /path/$uri` is wrong). `alias` replaces location prefix.

### Nginx reload and stale PID files

`nginx -s reload` reads the pid from `pid` directive in `nginx.conf` or a mismatched field. On Oracle Linux and similar distros, `/var/run/nginx.pid` can be empty after a careless rewrite. Fix:

```bash
sudo bash -lc 'echo <masterPID> > /var/run/nginx.pid'
```

where `<masterPID>` is the nginx master PID (e.g., from `pgrep -x nginx | head -1` or `ps aux | grep '[n]ginx: master'`).

### `include /etc/nginx/conf.d/*.conf` duplicate `server_name _` blocks

`/etc/nginx/nginx.conf` includes `/etc/nginx/conf.d/*.conf`. If both the main config and one of those includes declare `server_name _;`, nginx logs `conflicting server name "_" ... ignored` and depending on ordering your project location can become unreachable even when `nginx -t` passes.

Fix by making the project server the single authoritative block for that host, or by removing the duplicate matching server block. On Oracle Linux this surface showed up as 404/502 behavior under `/api/v1/` and `/projects/<name>/` with no `nginx -t` failures.

### Port 80 already in use

If `nginx` is already running, bind fails. Use the existing process via `reload`, do not start a second master.

### Frontend `base`

Without matching `base`, browsers request `/assets/...` instead of `/projects/<name>/assets/...` and get nginx 404.

## Public IP discovery

To identify the public IP, prefer user-provided values, a domain name, or metadata like:

```bash
curl -s https://ifconfig.me
```

If the metadata endpoint returns a security prompt, fall back to `ifconfig.me`.

## Output requirements

After confirming smoke tests pass, answer the user with the **full URL** they should open:

```
http://<publicIP>/projects/<projectName>/
```

If the user wanted `/wiki/api/v1/*` as a public alias, mention that too.
