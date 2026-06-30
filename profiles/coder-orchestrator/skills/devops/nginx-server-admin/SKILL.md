---
name: nginx-server-admin
description: Administer the nginx web server on the user's Oracle Cloud instance — SSL/HTTPS setup, port and firewall management (two-layer ufw + OCI Security List), project routing config, and deployment verification. Use when the user asks to enable HTTPS, open ports, configure SSL certs, add or modify nginx routes, or troubleshoot public access issues.
---

# Nginx Server Admin

Administer nginx and network access on the user's Oracle Cloud instance (IP `168.110.213.104`).

## Server Layout

- **nginx config**: `/etc/nginx/nginx.conf` includes `/etc/nginx/projects/*.conf`
- **Active project config**: `/etc/nginx/projects/default.conf` — single `server` block with path-based routing under `/projects/<slug>/`
- **Static project files**: `/var/www/html/projects/<slug>/`
- **PRD/review HTML files**: `/usr/share/nginx/html/prds/` (served at `/prd/<name>`)
- **Project API backends**: each project's Go/Node API runs on a localhost port (e.g. socialzen=8089, komuna=8095, self-flow=8096), proxied via `location ^~ /projects/<slug>/api/`
- **SSL certs**: `/etc/nginx/ssl/selfsigned.crt` + `.key` (self-signed, 365-day expiry)

## Oracle Cloud Two-Layer Firewall (critical)

This server has **two independent firewalls**. Both must allow a port for public access:

1. **OS-level (ufw)** — `sudo ufw allow <port>/tcp`. You manage this from the terminal.
2. **Network-level (OCI Security List)** — configured in the Oracle Cloud Console, NOT from the server. See `references/oracle-cloud-security-list.md` for exact steps.

**Diagnostic pattern**: If `curl http://localhost:<port>/` works but `curl http://168.110.213.104:<port>/` times out (not "connection refused", but hangs), the OCI Security List is blocking the port. ufw is open but the network firewall is not.

Port 80 was pre-opened in both layers. New ports (e.g. 443) need both.

## Enabling HTTPS

### Self-Signed Cert (bare IP, no domain)

Use when the user has no domain name and accepts browser warnings.

```bash
# 1. Generate cert (include IP as SAN)
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/CN=168.110.213.104" \
  -addext "subjectAltName=IP:168.110.213.104"

# 2. Add listen 443 ssl to the server block in /etc/nginx/projects/default.conf
#    Add these lines after the existing listen 80 directives:
#    listen 443 ssl;
#    listen [::]:443 ssl;
#    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
#    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
# Use sudo perl -0777 -i -pe for multiline edits (patch tool refuses system paths)

# 3. Open ufw
sudo ufw allow 443/tcp

# 4. Test and reload
sudo nginx -t && sudo systemctl reload nginx

# 5. Verify locally (bypasses OCI firewall)
curl -k https://localhost/health
curl -k -o /dev/null -w "%{http_code}" https://localhost/projects/socialzen/
```

After server-side setup, the user must open port 443 in the OCI Security List (see `references/oracle-cloud-security-list.md`).

### Let's Encrypt (requires a domain)

Use when the user has a domain pointed at `168.110.213.104`. Free, auto-renewing, no browser warnings.

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d <domain>
# Certbot auto-edits nginx config and sets up renewal timer
```

Let's Encrypt cannot issue certs for bare IP addresses — a domain is required.

## Adding a New Project Route

To serve a new project under `/projects/<slug>/`:

1. Build the frontend, copy to `/var/www/html/projects/<slug>/`
2. Add a `location` block to `/etc/nginx/projects/default.conf`:
   ```nginx
   location = /projects/<slug> { return 301 /projects/<slug>/; }
   location /projects/<slug>/ {
       alias /var/www/html/projects/<slug>/;
       index index.html;
       try_files $uri $uri/ /projects/<slug>/index.html;
   }
   ```
3. If the project has an API, add a proxy block:
   ```nginx
   location ^~ /projects/<slug>/api/ {
       proxy_pass http://127.0.0.1:<port>/api/;
       proxy_http_version 1.1;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```
4. `sudo nginx -t && sudo systemctl reload nginx`
5. Verify: `curl -o /dev/null -w "%{http_code}" http://localhost/projects/<slug>/`

## Editing System nginx Configs

The `patch` tool refuses to write to `/etc/nginx/`. Use terminal with `sudo`:
- Single-line edits: `sudo sed -i 's/old/new/' /etc/nginx/projects/default.conf`
- Multiline edits: `sudo perl -0777 -i -pe 's/old/new/' /etc/nginx/projects/default.conf`
- Always back up first: `sudo cp /etc/nginx/projects/default.conf /etc/nginx/projects/default.conf.bak.$(date +%Y%m%d%H%M%S)`

## Pitfalls

- **Forgetting the OCI Security List**: Opening ufw alone is not enough. If public access times out but localhost works, the Security List is the blocker — you cannot fix it from the terminal.
- **Self-signed cert browser warnings**: Browsers show "Not Secure" / "Your connection is not private". Users must click Advanced then Proceed. This is expected, not a bug. Mention the upgrade path to Let's Encrypt if they get a domain.
- **Cert expiry**: Self-signed certs expire. Regenerate with the same openssl command or set up a calendar reminder. Let's Encrypt auto-renews via systemd timer.
- **nginx config syntax**: Always run `sudo nginx -t` before reload. A syntax error in the config will prevent nginx from starting on reload.

## References

- See `references/oracle-cloud-security-list.md` for step-by-step instructions to open a port in the OCI Security List (the network-level firewall that cannot be configured from the server).
