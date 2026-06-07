# Demo Nginx Config

## Working multi-project config (Ubuntu 24.04)

Nginx main config:
- Include only `/etc/nginx/projects/*.conf` in `http { ... }`.
- Do not include `sites-enabled` or `conf.d`.
- When replacing the whole `http` block, include `events { worker_connections 1024; }` or nginx will fail to start.
- Keep exactly one default server for port 80, otherwise tests fail with duplicate default server errors.

One file per project under `/etc/nginx/projects/<name>.conf`:
```nginx
server { listen 80; server_name _; root /var/www/html/projects/<name>/; try_files /index.html =404; }
server { listen 89; server_name _; root /var/www/html/projects/insta-scheduler/; try_files /index.html =404; }
```

Document roots:
- If `/usr/share/nginx/html` does not exist, use `/var/www/html/projects/<name>` for static assets instead.
- Ensure `index.html` exists at the root of each project path; `try_files /index.html =404;` is enough for static React apps without an API proxy on that port.
- Do not mix `alias` with path-prefixed `root` locations unless you need nested mounts.

## Deployment checklist
1. `sudo nginx -t` must pass before `systemctl restart nginx`.
2. Run `sudo systemctl restart nginx` after changing ports or server blocks.
3. Verify each static endpoint with `curl -I -s http://127.0.0.1/<port>/index.html`.
4. Verify from public IP with `curl -I -s http://<publicIP>/`.

## apt/dpkg stuck locks on fresh Ubuntu 24.04
- If `apt-get update` fails with `/var/lib/dpkg/lock-frontend` while no apt process appears in `ps`, remove the stale locks and reconfigure dpkg:
  `sudo rm -f /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock`
  `sudo dpkg --configure -a`
  `sudo apt-get update`
- If a third-party repo key is missing, remove the offending source file instead of importing keys.

## Observed failure modes
- `stat() ... Permission denied` on user home paths: copy built frontend into `/var/www/html/projects/<projectName>/` so www-data can read it.
- `no "events" section in configuration`: replacing the full `http` block without `events { worker_connections ...; }` breaks startup.
- Multiple `listen 80 default_server` blocks across included `.conf` files cause `nginx: configuration file /etc/nginx/nginx.conf test failed` with duplicate default server errors. Keep one authoritative default server.