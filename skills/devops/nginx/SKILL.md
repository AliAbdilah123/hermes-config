---
name: nginx
description: Nginx serving, aliases, and nginx-level 404 troubleshooting for static projects and shared path prefixes
---

# Nginx

Use for exposing paths, fixing 404s under `/projects/`, `/prds/`, or other nginx prefixes, and auditing `alias` vs `root` path mismatches.

## References

- `references/config.md` — session-specific nginx + PHP-FPM layout on this host, alias pitfalls, `shell_exec` permission requirements, and current project-to-port proxy map.

## Procedure

1. Read config sources first: `/etc/nginx/nginx.conf`, `/etc/nginx/projects/*.conf`
2. Inspect the filesystem roots where sites actually exist.
3. Test current URLs with `curl -I` against the public IP/hostname.
4. Make edits with `patch`, then validate with `sudo nginx -t` and reload with `sudo systemctl reload nginx`.
5. Re-test the failing URL before adding rewrite variants.

## Key pitfalls

- `alias` URIs must end with a slash when the location also ends with one.
- Keep more-specific location blocks above generic prefixes.
- A catch-all `return 404` can mask newly added project slugs.
- Multiple possible roots: both `/usr/share/nginx/html/` and `/var/www/html/` have been used historically.
- `include /etc/nginx/projects/*.conf;` lives inside the `http` block in `nginx.conf`. Whether these files can contain bare `location` blocks depends on the include context: if included directly under `http`, they need a wrapping `server { ... }`; if the include directive itself is inside a `server` block (as in some setups), they can contain bare `location` blocks. When in doubt, add the new `location` block directly into an existing `server { ... }` file rather than creating a new top-level included config.
- For PHP under an `alias` path, **do not** nest `location ~ \\.php$` inside the `alias` `location`. Either `try_files` will fail or `SCRIPT_FILENAME` resolves off the wrong root. Instead, add a sibling regex block such as `location ~ ^/prefix/(.+\\.php)$` and point it at the real filesystem path: `fastcgi_param SCRIPT_FILENAME /var/www/html/prefix/$1;`.
- When PHP pages call `shell_exec()` for binaries in `$HOME`, `www-data` cannot traverse `$HOME` (usually `0700`). Fix by `chmod o+x /home/ubuntu` and parent dirs, or by installing a globally traversable wrapper in `/usr/local/bin` that suppresses stderr if needed.
- **Rebuild after project rename**: Renaming a project slug served under `/projects/<old>/` to `/projects/<new>/` requires **four synchronized changes**, or the page will fail silently:
  1. Update Vite `base` in `frontend/vite.config.ts`.
  2. Update API base path strings in the React app (typically `src/App.tsx` or similar).
  3. Update Go `serveReact(...)` path + any compiled-in static-root strings in the backend source, then rebuild.
  4. Update nginx `location` and `proxy_pass` prefixes.
  Missing any one of these produces a blank page or 404s that can be hard to spot because the root HTML itself loads fine.
- **Compiled Go static path**: Go backends often have a hardcoded frontend/dist path (e.g. `serveReact("/home/opc/system/frontend/dist")`). After renaming a project or restoring from backup, grep the backend source for the old path before rebuilding.
- **User-systemd `status=216/GROUP`**: In `~/.config/systemd/user/*.service`, do **not** include `User=ubuntu`. User services already run as the owning user; adding `User=` causes systemd to try group resolution and fail with `216/GROUP`, then auto-restart-loop.
- After deploying new assets, ensure ownership is correct: `sudo chown -R www-data:www-data /var/www/html/projects/<name>/`.

## Useful patterns

- **Expandable monitoring dashboards**: Use `<details>`/`<summary>` for process tables so the main page stays clean. Works on plain HTML without JS.
- **Memory ground truth**: `/proc/meminfo` reflects what the hypervisor currently presents. After a cloud resize, if the reported `MemTotal` is still the old size, the OS needs a reboot to pick up the new memory map.
- **Go backend + React frontend under `/projects/<name>/`**:
  1. Build the frontend (`npm run build`).
  2. Copy/sync the `dist/` contents into `/var/www/html/projects/<name>/` (owned by `www-data`).
  3. Update the Go binary or its source to serve the matching local `frontend/dist` path if it has one baked in.
  4. Add nginx locations in an existing `server { ... }` block:
     - `location ^~ /projects/<name>/api/v1/ { proxy_pass http://127.0.0.1:PORT/api/v1/; ... }`
     - `location ^~ /projects/<name>/ { alias /var/www/html/projects/<name>/; index index.html; try_files ...; }`
  5. Reload nginx, then start the backend on the proxied port binding to `127.0.0.1`.

## Frontend performance: split fast vs slow queries

For dashboards that include a heavy filesystem walk, the page renders immediately with skeleton loaders by splitting the data fetching:

1. **Fast stats** (`/api/v1/device`): loaded first in a dedicated `useEffect`, renders CPU/Memory/Disk immediately.
2. **Slow data** (`/api/v1/top/processes`, `/api/v1/top/files`, `/api/v1/top/cpu`): loaded in a second `useEffect` in the background, with per-table loading states.
3. **Backend optimization**: skip known-cache/hidden directories inside the filesystem walk to reduce I/O on large `/home` trees. In Go:
   - maintain a `skipDirs` map of directory names to skip (`.cache`, `.npm`, `.config`, `.local`, `.cargo`, `.rustup`)
   - skip any entry starting with `.` (except `.` itself) to avoid hidden caches
4. **Poll independently** — or use the same 3s interval for both; the UI shows different loading states so slow queries don't block the fast card updates.

## Go backend pattern for system stats

Endpoints to implement:
- `GET /api/v1/device` → total/used memory (MB), total/used disk (bytes), CPU % from `/proc/stat` delta
- `GET /api/v1/top/processes?limit=N` → sorted by memory (`ps aux --sort=-%mem`), includes PID, name, mem%, cpu%, RSS
- `GET /api/v1/top/cpu?limit=N` → sorted by CPU (`ps aux --sort=-%cpu`), same fields
- `GET /api/v1/top/files?limit=N` → filesystem walk with skip-list, sorted descending by size

Serve the React app from a hardcoded `frontend/dist` path with a `serveReact` handler that falls back to `index.html`.
