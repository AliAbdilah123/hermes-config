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

## Project-to-port map (observed 2026-06-26)

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

Add new `location ^~` blocks into the existing `server` block in `/etc/nginx/projects/default.conf`. Validate with `sudo nginx -t` and reload with `sudo systemctl reload nginx`.

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
