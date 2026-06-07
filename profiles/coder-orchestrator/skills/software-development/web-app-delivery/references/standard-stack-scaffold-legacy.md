# Legacy skill package: `standard-stack-scaffold`

This file preserves the former `standard-stack-scaffold` SKILL.md after consolidation into `web-app-delivery`. Relative support-file links have been rewritten to the re-homed files under `web-app-delivery`.

---

---
name: standard-stack-scaffold
title: Standard Fullstack Scaffolding (Go + React + SQLite)
description: >
  Create and serve a fullstack project using the default stack unless otherwise
  specified: frontend = TypeScript/React (Vite build), backend = Go with APIs
  under /api/v1/*, database = SQLite. Includes building, running, nginx proxy setup,
  and producing a public clickable URL.
triggers:
  - create project
  - new fullstack app
  - scaffold app
  - build with go react sqlite
  - serve project
  - make app public
  - nginx config for project
  - public IP/URL after deploy
---

# Standard Fullstack Scaffolding

Build a working fullstack app with this fixed default stack, serve it, add nginx
exposure, and give the user a direct clickable link using the actual public IP.

When writing URLs for the user, always substitute the real public IP.
Never return placeholder text such as `<publicIP>` or `public-ip`.
Preferred forms:
- http://<actual_public_ip>/projects/<project_name>/
- http://<actual_public_ip>/projects/<project_name>/api/v1/<endpoint>

## Stack Contract

- Frontend: TypeScript + React via Vite, built to `frontend/dist`
- Backend: Go HTTP server
- Routes: `/api/v1/*` must be reserved for APIs, and ALSO expose the same API
  under `/projects/<projectName>/api/v1/*`. Every other path serves the React
  build.
- Database: SQLite file under `backend/data.db`
- Public path: `<publicIP>/projects/<projectName>` via nginx

## Project Layout

Use this exact layout so the steps below stay consistent.

```
/projects/<projectName>/
  frontend/
    src/
    dist/
    vite.config.ts
  backend/
    main.go
    go.mod
    data.db
```

## Step-by-step

### 1. Frontend

If creating the `frontend/` directory would collide with prior scaffold debris, remove it first:
```bash
rm -rf frontend && mkdir -p frontend
```

Then scaffold:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
```

If the scaffold fails (commonly `Operation cancelled`), confirm `frontend/` doesn't already contain stale files, then rerun the same scaffold command. Only escalate to an alternate template after the path is clean.

Set `base` in `vite.config.ts` so assets resolve under the project path:
```ts
export default defineConfig({ base: '/projects/<projectName>/', plugins: [react()] })
```

High-complexity calendar deps are optional. Prefer a custom lightweight calendar rather than `react-big-calendar`/`date-fns` when those packages are creating toolchain or bundling blockers. If the user explicitly requests `react-big-calendar`, keep TS and fix TS/build errors in-place; update `tsconfig.app.json` as needed and do not switch to JS.

Build when ready:
```bash
npm run build
```

Use the project path directly in any user-facing deployment presentation
instead of inventing a placeholder. Do not say “public-ip” if you have not
actually fetched it. If the runtime contract requires an external access link,
substitute the real public IP/host.

### 2. Backend

Requirements:
- Go may not be in PATH on this host. Use `/home/opc/.local/go/bin/go` or
  equivalent local install. Do not assume system package access.
- Do not `go:embed` symlinks. Copy `frontend/dist` if you need to bundle it.
- SQLite driver: `modernc.org/sqlite`.
- Register `/api/v1/*` handlers BEFORE the catch-all frontend/file handler.
- Respect `PORT` env var, default `8080`.
- Bind to `127.0.0.1:8080` by default.

Build and run:

```bash
cd backend
go mod init <projectName>
go get modernc.org/sqlite
go build -o server main.go
./server
```

### 3. Public Exposure (Nginx)

Prefer drop-in files under `/etc/nginx/conf.d/<projectName>.conf`.
- Do not replace the system `nginx.conf` unless necessary.
- On Oracle Linux, clear stale `/etc/nginx/default.d/*.conf` files that duplicate
  port 80 or root `/api/v1` behavior before reloading.
- **Do not create a separate `server { listen 80; server_name _; }` block if one
  already exists.** On this host, `/etc/nginx/conf.d/demo.conf` already owns
  port 80. Instead, append `location /projects/<project>/api/v1/` and
  `location /projects/<project>/` blocks into the existing default_server config.
- After `nginx -t`, if you see `conflicting server_name "_"`, it means a
  duplicate server block was added. Remove the duplicate file and reload, or
  merge routes into the existing block.
- `sudo` on this host is not guaranteed non-interactive.
- When sending nginx config over SSH and then applying it, use the old config as
  the reference point instead of assuming the remote file is unchanged.

Config skeleton:

```nginx
server {
  listen 80;
  server_name _;

  location /api/v1/ {
    proxy_pass http://127.0.0.1:8080/api/v1/;
  }

  location /projects/<projectName>/api/v1/ {
    proxy_pass http://127.0.0.1:8080/api/v1/;
  }

  location /projects/<projectName>/ {
    root /usr/share/nginx/html;
    index index.html;
    try_files $uri $uri/ /projects/<projectName>/index.html;
  }
}
```

SELinux is a common hidden blocker on this host. After enabling
`httpd_can_network_connect`, serve built frontend assets from
`/usr/share/nginx/html/projects/<project>/` with `nginx:nginx` ownership. That
is more reliable than changing permissions or contexts on the original build
directory under the user home.

Reload:

```bash
sudo nginx -t && sudo nginx -s reload
```

On this host, `sudo` may not be fully non-interactive. If needed, ask the user
to supply the reload or sudo access.

### 4. Verify

Check from the host:
```bash
curl -s http://127.0.0.1:8080/api/v1/<endpoint>
curl -s http://127.0.0.1/projects/<projectName>/
curl -s http://127.0.0.1/projects/<projectName>/api/v1/<endpoint>
```

If the user asks whether a previous step was used, you can say yes. Avoid
re-executing roles or administrative flows that have already completed. Confirm
only whether they were applied and, if relevant, what outcome was produced.

### 5. Handoff

Give one clear clickable URL:
- Frontend: `http://168.110.196.49/projects/<projectName>/`
- API: `http://<actual_public_ip>/projects/demo/api/v1/hello`

If asked whether you “actually did this,” answer from the persisted project
state/output/files/config, not by regenerating or re-running the whole flow
unless verification is specifically requested.

## Stack lock rule

Once the user picks the default stack, do not silently change it. If the agreed stack is TS/React + Go + SQLite:
- Do not rewrite the backend in Python.
- Do not replace the frontend with HTML/JS unless the user explicitly asks.
- If build errors occur, fix the current stack first. Stack substitution is a last resort and must be user-approved.

Hard fallbacks only after user approval:
- For Go backend failures caused by the local Go toolchain/setup, ask whether a Python FastAPI fallback is acceptable.
- For React TS build failures, ask before switching to plain HTML/JS.

- `go:embed` with symlinks: fails with `cannot embed irregular file`. Copy the
  dist directory instead of symlinking.
- Frontend `base` missing: rebuilt assets return 404 under `/projects/<name>/`.
- Go missing: use local install `/home/opc/.local/go`.
- Nginx config path: use `/etc/nginx/conf.d/*.conf` for project configs.
- `httpd_can_network_connect` off: setsebool -P httpd_can_network_connect on
- `/etc/nginx/default.d/` may contain stale copies of project server blocks on
  Oracle Linux.
- Port 8080 occupied: assign the Go backend to another local port and update the
  nginx proxy_pass target. See `references/standard-stack-scaffold-port-sharing-lessons.md`.
- Frontend APIs should be called with the serving prefix: `/projects/<project>/api/v1/...`
  or a relative prefix that matches the base path.
- CPU sampling from `/proc/stat` must be primed once before the first delta,
  otherwise the first API call returns 0%.
- `sudo` on this host is not guaranteed non-interactive.
- When sending nginx config over SSH and then applying it, use the old config as
  the reference point instead of assuming the remote file is unchanged.
