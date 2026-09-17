# Subpath SPA API and authentication deployment

Use when a static SPA is served below a prefix such as `/projects/app/` and its same-origin API must live under that same prefix.

## Deployment chain

1. Build with the real SPA base prefix and inspect emitted HTML/assets.
2. Ensure the browser API client resolves requests from the deployed document base. Do not assume Vite `BASE_URL` mirrors a framework router base; prove the actual browser request URL.
3. If using `document.baseURI`, emit an explicit `<base href="<router-base>/">` and construct API URLs relative to it (for example `new URL('./api/...', document.baseURI)`).
4. Add an nginx API location that is more specific than the static SPA fallback, then proxy to a dedicated local listener.
5. Before selecting the listener, inspect current socket ownership. A successful health response from an occupied port may belong to an unrelated service.
6. Verify the exact systemd `ExecStart`, service-active state, local health payload, public prefixed health endpoint, public HTML asset hash, and browser network request URL independently.

## Logout robustness

Logout is a session-destruction operation. If it requires a client-readable CSRF token, stale or missing client state can prevent server-side invalidation while the UI still navigates to Sign In. Prefer a same-origin POST logout contract that authenticates via the HttpOnly session cookie and does not depend on a separate CSRF value, while retaining CSRF protection for state-changing business operations. Test server session deletion, cookie expiry, refresh after logout, a protected route in a new tab, and subsequent real login.

## Browser harness discipline

- Capture every response with status >= 400 and include its URL; generic UI copy often hides a wrong-prefix 404.
- After a locator failure, inspect accessible names. A `Password` label may also match a `Show password` button; use exact labels or stable IDs and replay the full flow with a fresh user.
- Verify one-account-per-platform behavior across add, hidden duplicate option, logout/login, reload persistence, remove, and re-add.
