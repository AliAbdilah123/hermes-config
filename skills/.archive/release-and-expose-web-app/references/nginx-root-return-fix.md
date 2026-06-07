# Root-return nginx fix on this host

Environment facts that avoid re-discovery later.

- Default include in `/etc/nginx/nginx.conf`: `include /etc/nginx/projects/*.conf;`
- `/etc/nginx/conf.d/` and `/etc/nginx/sites-enabled/` exist but are empty by default on this host.
- Authoritative default server block lives in `/etc/nginx/projects/default.conf`.
- Writing to `/etc/nginx/projects/default.conf` requires sudo; plain redirection will fail with permission denied.
- Reload path: `sudo nginx -t && sudo nginx -s reload`

## Standard patch pattern for a root text response

Replace the existing root `server` block in `/etc/nginx/projects/default.conf` rather than adding a new server block, to avoid duplicate `default_server` issues:

```bash
sudo bash -lc 'cat >/etc/nginx/projects/default.conf <<"EOF"
server {
    listen 80 default_server;
    server_name _;
    root /usr/share/nginx/html;

    location / {
        default_type text/plain;
        return 200 "<body>";
    }
}
EOF
nginx -t && nginx -s reload && curl -s http://127.0.0.1/'
```

## Verification order

1. `curl -s http://127.0.0.1/` returns the expected body.
2. Restart/reload still works without duplicate-server warnings.

## Pitfall

- `nginx: [emerg] open() "/run/nginx.pid" failed (13: Permission denied)` during reload means the command was not run under sudo.
- If `nginx -t` succeeds but the response is still 404, inspect whether another default server is present; on this host, the expected behavior is that the block in `/etc/nginx/projects/default.conf` handles `/`.
