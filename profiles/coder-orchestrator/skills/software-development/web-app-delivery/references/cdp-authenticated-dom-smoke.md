# Authenticated DOM Smoke via Chrome DevTools Protocol

Use this when the normal browser tool times out or is too heavy, but a deployed React app needs an authenticated UI smoke check. This is a deterministic fallback, not a replacement for full visual QA.

## Pattern

1. Start host Chromium/headless with a remote debugging port and origin allowance:

```bash
/usr/bin/chromium-browser \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --remote-allow-origins='*' \
  --remote-debugging-port=9336 \
  --user-data-dir=/tmp/chrome-smoke-9336 \
  about:blank
```

2. Connect to `http://127.0.0.1:<port>/json`, choose the first `type == "page"` target, then connect to its `webSocketDebuggerUrl` using Python `websocket-client`.

3. Enable `Page` and `Runtime`, navigate to the deployed route, and use `Runtime.evaluate` to run the real login flow:

```js
fetch('/projects/<project>/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  credentials: 'include',
  body: JSON.stringify({username: 'admin', password: '<password>'})
}).then(r => r.json()).then(j => {
  localStorage.setItem('csrf', j.csrfToken)
  return !!j.csrfToken
})
```

4. Navigate/reload the app, click the target nav/button via DOM JS, then assert exact user-facing strings:

```js
[...document.querySelectorAll('button')]
  .find(b => b.textContent.includes('Scripts'))?.click()

document.body.innerText.includes('Template Outreach')
document.body.innerText.includes('Buat Template')
document.body.innerText.includes('{{business.name}}')
```

## Pitfalls

- If WebSocket handshake returns 403, restart Chromium with `--remote-allow-origins='*'`.
- Avoid attaching to extension/background targets; filter `/json` targets for `type == "page"`.
- If the app is served through nginx, navigate to the nginx URL (`http://localhost/projects/<project>/...`) and use project-prefixed API paths so cookies, base paths, and proxies match production behavior.
- Do not accept the login screen as proof of authenticated UI. Authenticate, reload, navigate to the feature route, and assert feature-specific text.
- After `npm run build`, compare `dist/index.html` asset hashes with the nginx-served index. If stale, copy/sync `dist/` to the web root before DOM checks.
