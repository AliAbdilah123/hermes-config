# SocialZen Inline UI Autocomplete on the Go/SQLite Stack

Use this reference when a SocialZen feature plan describes the old Cloudflare Worker/TypeScript/KV architecture but the checked-out/live project is the local Go/SQLite + Vite stack.

## Architecture translation

- Backend route work usually belongs in `apps/backend-go/main.go`, not `apps/backend/src/routes/*`.
- Frontend work remains in `apps/frontend/src/*`.
- If a plan calls for Cloudflare KV caching, implement the equivalent local server-side cache in Go when SocialZen is running as the Go service. Keep the semantics (TTL, graceful fallback, cache-hit not counting as upstream API work), but do not invent Cloudflare bindings in the local stack.
- For inline autocomplete features, keep frontend API types/client in the existing domain client (for hashtags, `apps/frontend/src/lib/instagram.ts`) and add the React component under `apps/frontend/src/components/` only when there is no existing component to extend.

## Verification commands that match this stack

From repo root:

```bash
pnpm --filter frontend typecheck
pnpm --filter frontend test
pnpm --filter frontend build
```

Backend commands must run from the Go module directory:

```bash
cd apps/backend-go && go test ./...
cd apps/backend-go && go build ./...
```

Do not run `go build ./...` from the repo root unless a root `go.mod` exists; SocialZen's Go module is currently under `apps/backend-go`.

## Deployment sequence

Before deploying, confirm the active web root and service rather than relying on docs:

```bash
grep -R "socialzen" -n /etc/nginx 2>/dev/null | head
systemctl show socialzen -p FragmentPath -p ExecStart -p EnvironmentFiles -p ActiveState --no-pager
```

Known current deployment shape:

- API service: `socialzen.service`
- Backend binary: `/opt/socialzen/socialzen-server`
- Frontend alias: `/var/www/html/projects/socialzen/`
- Service env file: `/home/ubuntu/socialzen/.env` (do not print secrets)

Deploy after successful local tests/builds:

```bash
mkdir -p /tmp/socialzen-deploy
(cd apps/backend-go && GOOS=linux GOARCH=arm64 go build -o /tmp/socialzen-deploy/socialzen-server .)
sudo install -m 0755 /tmp/socialzen-deploy/socialzen-server /opt/socialzen/socialzen-server
sudo rsync -a --delete apps/frontend/dist/ /var/www/html/projects/socialzen/
sudo systemctl restart socialzen
systemctl is-active socialzen
curl -fsS -o /tmp/socialzen-index.html -w 'index:%{http_code}\n' http://127.0.0.1/projects/socialzen/
asset=$(grep -o 'assets/index-[^" ]*\.js' /tmp/socialzen-index.html | head -1)
curl -fsS -o /dev/null -w 'asset:%{http_code}\n' "http://127.0.0.1/projects/socialzen/$asset"
```

## Headless browser QA fallback

If the browser tool times out and Playwright is not installed, Chromium can still be driven through Chrome DevTools Protocol without adding dependencies:

1. Start `/usr/bin/chromium-browser --headless=new --no-sandbox --remote-debugging-port=<port> --user-data-dir=/tmp/<qa-profile> about:blank`.
2. Fetch `http://127.0.0.1:<port>/json/version` for the browser websocket URL.
3. Use Node's built-in `WebSocket` to call CDP methods (`Target.createTarget`, `Page.navigate`, `Runtime.evaluate`, `Input.insertText`, `Input.dispatchKeyEvent`).
4. Set the `brand_session=demo-session` cookie with `Network.setCookie` before navigating to protected app routes.
5. Assert DOM state with `Runtime.evaluate`; keep the script as a temporary QA artifact unless it becomes generally reusable.

This is especially useful for verifying UI behaviors like debounced autocomplete, dropdown insertion, keyboard dismissal, and no-trigger edge cases without introducing test dependencies.
