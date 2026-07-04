# Restricted Route Auth Guards

## Problem pattern

Komuna's Go API has a convenience `currentUser(r)` helper that falls back to the configured demo/default user when no real session exists. That is useful for demo/public-ish flows, but it is unsafe for restricted pages and account data.

If a restricted handler calls `currentUser(r)` directly, unauthenticated requests can return `200 OK` with demo/default-user data instead of `401`, and the React page may render an error/empty/demo state instead of redirecting to login.

## Backend fix pattern

Use a strict helper for restricted handlers:

```go
func (a *App) requireUser(w http.ResponseWriter, r *http.Request) (authUser, bool) {
    if uid := r.Header.Get("X-Komuna-User"); uid != "" {
        return authUser{ID: uid, Email: uid + "@komuna.local", Name: uid}, true
    }
    u, ok := a.userFromRequest(r)
    if !ok {
        errOut(w, 401, "auth_required")
        return authUser{}, false
    }
    return u, true
}
```

Then at the top of any restricted handler:

```go
u, ok := a.requireUser(w, r)
if !ok {
    return
}
uid := u.ID
```

Do **not** use `currentUser(r)` for:
- `/me/workspace`
- `/wallet`
- `/purchases`
- `/my/bookings`
- `/notifications*`
- `/profile/*`
- `/platform/dashboard`
- program admin/member/manage dashboard/data routes
- purchase/claim/checkout mutation routes

`currentUser(r)` can remain only where the route is intentionally demo/public-compatible.

## Frontend fix pattern

Direct top-level restricted React routes also need an auth wrapper. Backend `401` protects data, but the user experience should redirect to login instead of rendering page-level errors.

Minimal wrapper:

```tsx
function RequireAuth({ children }: { children: ReactNode }) {
  const session = authClient.useSession()
  if (session.isPending) return <main style={{ padding: 32 }}>Loading session...</main>
  if (!session.data) return <Navigate to="/auth/sign-in" replace />
  return <>{children}</>
}
```

Wrap direct restricted routes such as `/wallet`, `/my/bookings`, `/notifications`, `/settings/notifications`, and `/profile`. Workspace routes remain guarded by `WorkspaceRoute`.

## Regression test

Add a table-driven Go test that calls the restricted API paths without auth and expects `401 Unauthorized` for every one. Include at least:

```go
paths := []string{
    "/api/v1/me/workspace",
    "/api/v1/wallet",
    "/api/v1/purchases",
    "/api/v1/my/bookings",
    "/api/v1/notifications",
    "/api/v1/notifications/unread-count",
    "/api/v1/notifications/preferences",
    "/api/v1/profile/preferences",
    "/api/v1/platform/dashboard",
    "/api/v1/programs/prog-box/member/dashboard",
    "/api/v1/programs/prog-box/manage/products/prod-box/session-claims",
    "/api/v1/programs/prog-box/admin",
}
```

Preserve tests for endpoints that now require auth by adding an explicit test header/session (`X-Komuna-User` is acceptable for existing test fixtures).