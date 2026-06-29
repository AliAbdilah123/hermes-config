# SPA Subpath API Routing Triage

Use when a deployed SPA lives under a subpath such as `/projects/<app>/` and login/API actions show generic `request_failed`, 404, or network errors even though the backend service is healthy.

## Symptom pattern

- Direct proxied endpoint works: `/projects/<app>/api/v1/...` returns 200.
- Root-relative endpoint fails: `/api/v1/...` returns 404 or reaches the wrong app.
- Frontend source/build has helper logic that applies the Vite `base`, but API calls beginning with `/api/` may bypass it.

## Investigation recipe

1. Confirm the public mount and Nginx/proxy route:
   - Static app: `/projects/<app>/`
   - API proxy: `/projects/<app>/api/v1/` -> backend `/api/v1/`
2. Compare both URLs with curl:
   - `POST http://host/api/v1/auth/login` should fail if there is no root API.
   - `POST http://host/projects/<app>/api/v1/auth/login` should hit the intended backend.
3. Inspect the served production JS bundle, not only source:
   - Find the route builder/helper.
   - Confirm it prefixes `/projects/<app>/` for `/api/...` calls.
4. Browser-verify with network capture if possible:
   - Login request URL should be `/projects/<app>/api/v1/auth/login`.
   - Follow-up requests such as `/me` and workspace/data loads should also carry the subpath.

## Fix pattern

Do not special-case `path.startsWith('/api/')` to bypass `apiPath()`/base-path construction in production subpath deployments. Normalize all API paths through the same base-aware helper, for example:

```ts
function apiPath(path: string) {
  const base = import.meta.env.DEV ? '/' : import.meta.env.BASE_URL
  return `${base.endsWith('/') ? base : `${base}/`}${path.replace(/^\//, '')}`
}

async function apiJSON<T>(path: string, init: RequestInit = {}): Promise<T> {
  const requestPath = apiPath(path)
  const response = await fetch(requestPath, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init.headers ?? {}) },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(String(payload.error ?? 'request_failed'))
  return payload as T
}
```

## Verification checklist

- Build succeeds.
- Deployed `index.html` references the new hashed JS asset.
- Served JS includes the expected base path literal, e.g. `/projects/<app>/`.
- Served JS no longer contains an `/api/` bypass pattern.
- Public browser login succeeds and network requests target `/projects/<app>/api/...`.