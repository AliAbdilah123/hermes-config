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
- `include /etc/nginx/projects/*.conf;` lives inside the `http` block in `nginx.conf`. Files matched there **cannot** contain bare `location` blocks (only valid inside `server`/`location`). Add locations into an existing server-block file, or wrap them in a `server { ... }` block inside the included file.
- For PHP under an `alias` path, **do not** nest `location ~ \\.php$` inside the `alias` `location`. Either `try_files` will fail or `SCRIPT_FILENAME` resolves off the wrong root. Instead, add a sibling regex block such as `location ~ ^/prefix/(.+\\.php)$` and point it at the real filesystem path: `fastcgi_param SCRIPT_FILENAME /var/www/html/prefix/$1;`.
- When PHP pages call `shell_exec()` for binaries in `$HOME`, `www-data` cannot traverse `$HOME` (usually `0700`). Fix by `chmod o+x /home/ubuntu` and parent dirs, or by installing a globally traversable wrapper in `/usr/local/bin` that suppresses stderr if needed.

## Useful patterns

- **Expandable monitoring dashboards**: Use `<details>`/`<summary>` for process tables so the main page stays clean. Works on plain HTML without JS.
- **Memory ground truth**: `/proc/meminfo` reflects what the hypervisor currently presents. After a cloud resize, if the reported `MemTotal` is still the old size, the OS needs a reboot to pick up the new memory map.
