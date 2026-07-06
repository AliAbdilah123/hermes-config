# Session references: nginx + PHP-FPM on this host

## Config source layout

- `nginx.conf` includes `/etc/nginx/projects/*.conf` inside the `http` block.
- Projects-specific locations live in `/etc/nginx/projects/default.conf` (inside a single `server { ... }` block).
- New paths like `/system/` must be added **inside** an existing server-block file, not as a standalone `location` in a new `.conf` file matched by the `projects/*.conf` glob (nginx rejects `location` at `http` level).

## PHP-FPM snippet used

```nginx
location /system/ {
    alias /var/www/html/system/;
    index index.php;
    try_files $uri $uri/ /system/index.php;
}

location ~ ^/system/(.+\.php)$ {
    include fastcgi_params;
    fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    fastcgi_param SCRIPT_FILENAME /var/www/html/system/$1;
}
```

Rationale:
- `alias` paths and nested PHP locations do not play well; `try_files $uri $uri/ /system/index.php` keeps the `index.php` fallback, while the sibling regex block handles execution with the correct `SCRIPT_FILENAME`.

## `alias` gotchas observed

- `alias /var/www/html/system/;` inside `location /system/` works, but a nested `location ~ \.php$` with `fastcgi_param SCRIPT_FILENAME /var/www/html/system$fastcgi_script_name;` resolved to `/var/www/html/system/system/index.php` because `$fastcgi_script_name` still carried the original URI prefix.
- Workaround: compute the relative path with a regex capture and pass that into `SCRIPT_FILENAME`.

## shell_exec permission requirements observed

PHP `shell_exec()` runs as the `www-data` user, which lacks `$HOME` and access to user-local bins by default. For a binary at `/home/ubuntu/.local/bin/codex` to work:
1. The binary itself must be readable and traversable: `chmod o+x /home/ubuntu/.local/bin/codex` (and `o+x` on each parent directory if stricter).
2. The config/auth file (`/home/ubuntu/.codex/auth.json`) must be readable if the script reads it.
3. If the binary emits noisy startup warnings to stderr (e.g., Codex PATH alias warnings), wrap it in a script that redirects stderr: `/usr/local/bin/codex-wrapper` with `exec /home/ubuntu/.local/bin/codex "$@" 2>/dev/null`.

## Project-to-port map (observed 2026-06-30)

| Project | Nginx prefix | Upstream |
|---|---|---|
| fnb-pos | `/projects/fnb-pos/api/v1/` | `http://127.0.0.1:8080/api/v1/` |
| multitenant-auth-saas-boilerplate | `/projects/multitenant-auth-saas-boilerplate/api/v1/` | `http://127.0.0.1:8087/api/v1/` |
| brand-organizer | `/projects/brand-organizer/api/` | `http://127.0.0.1:8088/api/` |
| insta-scheduler | `/projects/insta-scheduler/api/v1/` | `http://127.0.0.1:8083/api/v1/` |
| local-business-os-indonesia | `/projects/local-business-os-indonesia/api/v1/` | `http://127.0.0.1:8090/api/v1/` |
| local-business-os-indonesia healthz | `/projects/local-business-os-indonesia/healthz` | `http://127.0.0.1:8090/healthz` |
| siapjasa | `/projects/siapjasa/api/v1/` | `http://127.0.0.1:8094/api/v1/` |
| komuna-api | `/projects/Komuna/api/v1/` | `http://127.0.0.1:8091/api/v1/` |
| socialzen | `/projects/socialzen/api/` | `http://127.0.0.1:8089/api/` |
| server-monitor | `/projects/server-monitor/api/v1/` | `http://127.0.0.1:8081/api/v1/` |

Add new `location ^~` blocks into the existing `server` block in `/etc/nginx/projects/default.conf`. Validate with `sudo nginx -t` and reload with `sudo systemctl reload nginx`.

When deploying or renaming a Go backend serving a Vite-built React app:
1. Update `vite.config.ts` `base` to match the nginx prefix.
2. Update the React app's API fetch base path to the same prefix.
3. Grep the Go backend for any hardcoded frontend/dist paths (e.g. `serveReact("/home/opc/system/frontend/dist")`) and update to the new project directory.
4. Rebuild the Go binary.
5. Copy `frontend/dist/` contents into `/var/www/html/projects/<name>/` and `chown -R www-data:www-data`.
6. Add matching nginx `location ^~ /projects/<name>/ { alias ... try_files ... }` and `location ^~ /projects/<name>/api/v1/ { proxy_pass ... }`.
7. Start the Go server binding `127.0.0.1:PORT`.

Missing any of these produces a blank page because the HTML loads but asset scripts/CSS fetch from the wrong prefix.

## User systemd `status=216/GROUP` pitfall

For `~/.config/systemd/user/*.service`, do **not** add `User=ubuntu`. The service already runs as the owning user; adding `User=` causes systemd to attempt group resolution and fail with `status=216/GROUP`, then auto-restart-loop.

## Codex CLI status fields (v0.141.0)

Local state at `~/.codex/auth.json` contains:
- `auth_mode` (e.g., `chatgpt`, `api`)
- `OPENAI_API_KEY`
- `tokens` (id_token, access_token, refresh_token when using ChatGPT login)
- `last_refresh`

Quota windows (4h / weekly / monthly) are not exposed locally; they require the OpenAI account/usage page.

### `codex doctor --json`

Useful for surfacing warnings/errors from a PHP page or cron job. The output is JSON with `checks[]` where each item has `id`, `status`, `summary`, and `details`. Filter where `status` is `warning`, `error`, or `failed`.

Note: `codex login status` exits with code 1 when using ChatGPT-mode tokens even though the session is valid; detect login state by reading `auth.json` fields rather than relying on the exit code. Also suppress stderr (`2>/dev/null` or wrapper script) to avoid noisy PATH alias warnings in automated scripts.

## External healthcheck endpoints

The cheapest external probe is a static file served by nginx. Create once, never modify:

```bash
echo "ok-$(date +%s)" | sudo tee /usr/share/nginx/html/healthz.html
```

Configure your monitor to check `http://168.110.213.104/healthz.html` (or the equivalent domain). For Oracle Cloud Infrastructure, use the **OCI Monitoring Alarm** service or a low-cost external monitor (UptimeRobot, Kuma, Healthchecks.io).

If per-project health checks are wanted, add sibling static routes inside the existing `server { ... }` in `/etc/nginx/projects/default.conf`:

```nginx
location ^~ /healthz/ {
    alias /usr/share/nginx/html/healthz/;
    autoindex off;
}
# per-project healthz
location = /projects/server-monitor/healthz {
    proxy_pass http://127.0.0.1:8081/healthz;
    proxy_set_header Host $host;
}
```

## In-server vs out-of-server detection coverage

| Scenario | Detected by in-server watchdog | Detected by external HTTP probe |
|---|---|---|
| Load spike / soft stall | ✅ load > nproc flag | ❌ may still respond to TCP |
| Low memory / disk full | ✅ thresholds | ✅ often both |
| Service crash (9router, nginx, ssh) | ✅ systemctl probes | ✅ if monitor retries |
| fs stall (mmap / page-cache hang) | ✅ write-test `touch /tmp/` | ❌ may time out at TCP layer |
| Full network loss / host block | ❌ script can't run | ✅ TCP timeout triggers |
| Hypervisor freeze / reboot loop | ❌ | ✅ with long enough timeout |

Pair both probes. Point external probes at a nginx-served static path, not at an API endpoint that depends on upstream Go processes — those are exactly the things that go down together.

## Oracle `unified-monitoring-agent` "expected to be hung"

Oracle's agent repeats this log line when its own fluentd monitor is dead. Presence of this line without a restart attempt means the **OS itself did not restart the hung process** for a long window — a strong signal of system-wide stall rather than a single OOM or segfault. Do not treat "fluentd is hung" as a mono-failure; use it as evidence to widen the investigation to load, I/O, and watchdog fires on core services.
