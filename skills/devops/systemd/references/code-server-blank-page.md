# code-server blank/unreachable page checklist

Use when `http://<host>:8999/` returns a blank page or fails to load for an external client.

## First distinction: login page vs blank

- Local `curl http://127.0.0.1:8999/` returning `302 Found -> ./login` means the service is healthy; the browser is being redirected to the login form.
- A truly blank response from the same URL means code-server itself is failing to render.

## Network reachability order

1. `ss -tlnp | grep ':8999'` — confirm the port is actually listening.
2. `curl -sS --max-time 5 http://127.0.0.1:8999/ | head` — confirm local response.
3. `sudo ufw status verbose` — ensure `8999/tcp` is in the `To ... Action From` allow list.
4. `sudo nft list ruleset` / `sudo iptables -L -n` — check for explicit drops that run before UFW user-input rules (Tailscale `ts-input` drops on `100.64.0.0/10` are a known trap on this host).

## Tailscale CGNAT trap on this host

- Client IPs like `100.124.60.57` fall inside `100.64.0.0/10`.
- The `ts-input` chain drops `ip saddr 100.64.0.0/10 iifname != "tailscale0"` before UFW user-input is evaluated.
- Fix: either connect through `tailscale0`, or add a specific allow for the client IP before the broad CGNAT drop in `ts-input`, or use a non-CGNAT egress path.

## UFW allow pattern

```bash
sudo ufw allow 8999/tcp
sudo ufw allow 8999/tcp comment 'code-server'
sudo ufw reload
sudo ufw status verbose
```

## Quick validation

```bash
curl -sS -D - --max-time 10 http://127.0.0.1:8999/login?folder=/home/ubuntu/projects/<name> -o /tmp/cs-login.html
wc -c /tmp/cs-login.html
head -c 400 /tmp/cs-login.html
```

Expect `200 OK`, `text/html`, and a non-empty HTML body containing `code-server login`.

## Related

- `code-server-config-gotcha.md` — passing the open-folder path correctly via `ExecStart`.
