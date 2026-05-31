---
name: release-and-expose-web-app
description: >
  Deliver a TS/React + Go/SQLite project and make it publicly reachable via nginx.
  Covers: build, serve, nginx config, SELinux/perms checks, and production endpoint verification.
tags: [web, nginx, react, go, sqlite, release]
---

# Release and expose a web app

Use for:
- Shipping a fresh TS/React + Go/SQLite project built as requested.
- Making it reachable at `http://<publicIP>/projects/<projectName>`.

## 1. Implementation contract

- Frontend: TypeScript + React (Vite build), served statically.
- Backend: Go HTTP server, APIs under `/api/v1/*`, remaining paths serve the React build.
- Database: SQLite, created/auto-migrated in `backend/` on startup.
- Public path: nginx presents the app at `/projects/<projectName>`.

## 2. Build and serve order

1. `npm run build` in `frontend/`.
2. Start the Go server from `backend/` talking to `backend/data.db`.
3. Verify backend locally: `curl -I -s http://127.0.0.1:<PORT>/api/v1/hello` -> 200 before nginx verification.

Go server notes:
- Plain `:8080` for localhost testing; no auth required.
- Frontend: serve `frontend/dist` when request path is NOT `/api/v1*`.
- API paths: return JSON/HTML template depending on handler.
- Preferred fallback rule: if TS build is unreliable due to missing toolchain, deliver a plain HTML/JS frontend instead of forcing TypeScript.
- Calendar library fallback: if `react-big-calendar`/`date-fns` add build friction, replace with a custom lightweight JS calendar to avoid deadlock.
- Backend fallback: if the default Go stack fails due to local toolchain mismatch, prefer Python `uv` + `fastapi` with JSON file storage and the same API contract.

## Nginx config, deploy, and verification
- Use the existing default server block as the single source of truth for routing; avoid adding new standalone server blocks for a project when one already exists for `*:80`.
- Do not rely on a secondary include like `/etc/nginx/conf.d/*.conf` to add a new project block if your main config also defines a default server — move the project routes into the existing authoritative block instead to prevent duplicate default server errors.
- Confirm `/etc/nginx/nginx.conf` actually includes the config file you just wrote before reloading; if it doesn’t, the file is ignored.
- Preserve the original default-server config first, add the requested paths into it, then reload cleanly.
- Project-prefixed API path is the authoritative public path for this setup: `http://<publicIP>/projects/<projectName>/api/v1/*` for the backend and `http://<publicIP>/projects/<projectName>/` for the static app.
- Consistency rule for this environment: once the user confirms the default stack, do not deviate from it mid-delivery.

## 3. Nginx config

- Add the project server block into `/etc/nginx/conf.d/<project>.conf` as `default_server` for port 80.
- Avoid having another `listen 80 default_server` under `/etc/nginx/default.d/*.conf`; it creates duplicate‑server warnings and unpredictable routing.

Skeleton server block:
```
- The HTTP runtime exposes APIs at `<publicIP>/api/v1/*`, so that a residual `/api/v1/*` block on port 80 can be used as a compatibility alias for direct access in environments that rely on the root prefix.</n- If a project-prefixed API alias is also required, add the matching project-scoped proxy block alongside the root `/api/v1/` block so both paths work without dropping either.\n- Example combination: keep `/api/v1/` working for backward compatibility, and also expose `/projects/<name>/api/v1/` for project-scoped access.\n- SELinux Enforcing commonly blocks home-directory serving; deploy static assets into `/usr/share/nginx/html/<project>/` and ensure SELinux bools or directory permissions allow nginx access.\n- Having multiple `listen 80` `default_server` blocks across included `.conf` files produces unresolved warnings and unreliable routing.
```

## 4. Exposition path

Copy the React build into nginx’s web root and set ownership so SELinux and traversal are not blockers:

```
sudo mkdir -p /usr/share/nginx/html/<project>
sudo cp -r frontend/dist/* /usr/share/nginx/html/<project>/
sudo chown -R nginx:nginx /usr/share/nginx/html/<project>
sudo chmod -R o+rX /usr/share/nginx/html/<project>
sudo setsebool -P httpd_can_network_connect on  # if nginx proxies to backend
sudo nginx -t && sudo nginx -s reload
```

If serving from a non-root path instead, also ensure the path traverses for `nginx`/`others` and any required SELinux bools are enabled.

## 5. Verification order

1. Backend local: `curl -I -s http://127.0.0.1:8080/api/v1/hello` => 200.
2. Backend via nginx: `curl -I -s http://127.0.0.1/api/v1/hello` => 200.
3. Frontend via nginx: `curl -I -s http://127.0.0.1/projects/<name>/` => 200.
4. Any alternate path alias (e.g. `/wiki/api/v1/hello`) if present.

## 6. Deliverable

After checks pass, report one clickable link:
`http://<publicIP>/projects/<projectName>`

## 7. Pitfalls

- SELinux Enforcing is a common hidden blocker: use `/usr/share/nginx/html/<project>/` or enable related bools/paths.
- Having multiple `listen 80` `default_server` blocks across included `.conf` files produces “conflicting server name '_'” warnings and unreliable routing.
- Make sure `/projects/<name>/index.html` exists and is readable before relying on `try_files`.
- When editing root-owned nginx paths, use `sudo tee` or `sudo bash -c 'cat > ...'`.

## references/

- `oracle-linux-nginx-selinux.md`: checklist of SELinux + home-dir fixes for nginx on OL9.

