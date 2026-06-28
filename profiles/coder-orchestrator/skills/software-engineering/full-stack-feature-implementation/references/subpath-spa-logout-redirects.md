# Subpath SPA logout redirects

When a React/Vite SPA is deployed under a subpath such as `/projects/<app>/`, logout must not hard-redirect to `/` unless the host root is intentionally the app shell. On this user's project host, `/` may be a plain host-level health/default page (for example `hello`), while the app lives under its Vite `base` path.

## Pattern

1. Inspect `vite.config.ts` for `base` and the nginx alias/public path.
2. Find logout flows in shared helpers and UI callers (`signOut`, `logout`, `window.location`, `location.assign`, `navigate`).
3. Prefer redirecting signed-out users to an app route such as `/auth/sign-in`, then resolve it against `import.meta.env.BASE_URL`:

```ts
function getBasePath(base = import.meta.env.BASE_URL || '/'): string {
  return base.endsWith('/') ? base.slice(0, -1) : base
}

export function resolveSignedOutRoute(path = '/auth/sign-in', base = import.meta.env.BASE_URL || '/'): string {
  if (/^https?:\/\//i.test(path)) return path
  const basePath = getBasePath(base)
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  if (basePath && normalizedPath.startsWith(`${basePath}/`)) return normalizedPath
  if (normalizedPath === '/') return basePath ? `${basePath}/` : '/'
  return `${basePath}${normalizedPath}`
}

export function reloadSignedOutRoute(path = '/auth/sign-in') {
  window.location.assign(resolveSignedOutRoute(path))
}
```

4. Update callers to pass `/auth/sign-in` instead of `/` after successful sign-out.
5. Add tests for both the default logout caller and `resolveSignedOutRoute('/auth/sign-in', '/projects/<app>/')`.
6. After build/deploy, verify:
   - public index asset hash changed
   - `/` response is not confused with app behavior
   - `/projects/<app>/auth/sign-in` returns the SPA shell, not the host root page
   - deployed JS contains the expected app base path and signed-out route

## Pitfall

React Router `to="/"` is app-relative inside `BrowserRouter basename`, but `window.location.assign('/')` is host-root-relative. Shared hard reload helpers must explicitly account for the deployed base path.