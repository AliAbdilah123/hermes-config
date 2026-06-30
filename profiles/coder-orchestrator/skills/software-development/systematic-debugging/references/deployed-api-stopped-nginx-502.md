# Deployed API Stopped / Nginx 502 Triage

Use when a deployed SPA shows an API-load failure and the public API route returns `502 Bad Gateway`.

## Minimal evidence path

1. Confirm the browser-visible failure at the exact public API URL, not only the page UI:
   ```bash
   curl -i --max-time 5 http://<host>/projects/<app>/api/v1/programs
   ```
2. Check the expected upstream port directly:
   ```bash
   curl -i --max-time 5 http://127.0.0.1:<port>/api/v1/programs
   ss -ltnp | grep <port> || true
   ```
3. Check the app service state:
   ```bash
   systemctl status <app>-api.service --no-pager -l
   journalctl -u <app>-api.service -n 80 --no-pager
   ```
4. If the service is simply `inactive (dead)` and no live process is bound to the upstream port, restart it:
   ```bash
   sudo systemctl start <app>-api.service
   sleep 1
   systemctl status <app>-api.service --no-pager -l
   ```
5. Verify both internal and public routes return JSON `200 OK`:
   ```bash
   curl -i --max-time 5 http://127.0.0.1:<port>/api/v1/programs | head -40
   curl -i --max-time 5 http://<host>/projects/<app>/api/v1/programs | head -40
   ```

## Pitfalls

- Do not use the frontend's generic error copy as proof that the API code is broken; first distinguish stopped upstream (`502`) from application-level `4xx/5xx`.
- Verify the route prefix. A deployed subpath may expose `/projects/<app>/api/v1/...` while `/projects/<app>/api/...` or `/api/...` returns `404`.
- After restarting, check service state after a short delay so a crash loop is not mistaken for a successful restart.
