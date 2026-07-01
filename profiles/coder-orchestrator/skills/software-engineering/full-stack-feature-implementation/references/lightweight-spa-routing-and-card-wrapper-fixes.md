# Lightweight SPA routing and shared Card wrapper fixes

Use when a React/Vite app uses an in-house route state instead of React Router, and shared shadcn wrappers are retrofitted into an existing CSS system.

## Durable pattern

- If navigation changes page state but not the URL, do not add a router just for this. Wire the existing `routeTo()` helper to `window.history.pushState`, initialize route state from `window.location.pathname`, and subscribe to `popstate` for back/forward.
- For apps deployed under a Vite `base`/nginx subpath, strip `import.meta.env.BASE_URL` when deriving the current route and prepend it when pushing a new path.
- If a detail route needs selected in-memory data, handle hard reload gracefully by falling back to the list page instead of showing a broken blank/detail page.
- When a shared project `Card` component wraps shadcn `Card`, keep the legacy project card class (for example `.card`) in the wrapper unless all consumers have been migrated to explicit `CardHeader`/`CardContent`. Otherwise pages like profile/status cards lose their padding.
- Add a small DOM test that asserts URL path changes after clicking navigation; it catches regressions in state-only routing.

## Minimal implementation sketch

```tsx
const [route, setRoute] = useState<Route>(() => routeFromLocation())

useEffect(() => {
  const syncRoute = () => setRoute(routeFromLocation())
  window.addEventListener('popstate', syncRoute)
  return () => window.removeEventListener('popstate', syncRoute)
}, [])

function routeTo(nextRoute: Route) {
  setRoute(nextRoute)
  const nextPath = appRoutePath(nextRoute)
  if (window.location.pathname !== nextPath) window.history.pushState(null, '', nextPath)
}
```

Keep the diff small: use native History API first; add React Router only when nested routes, data loaders, route params, or broad route composition justify it.
