# Komuna Frontend Auth Guards

## Auth Architecture

The React SPA uses a **local auth client** (`apps/web/src/lib/auth.ts`) backed by the Go+SQLite API at `/api/v1/auth/*`. No Neon Auth.

### Session Store

- `localStorage` keys: `komuna.auth.token` (JWT), `komuna.auth.user` (JSON)
- `authClient.useSession()` returns `{ data: LocalAuthSession | null, isPending: boolean, error: Error | null }` via `useSyncExternalStore`
- On app load, if a token exists in localStorage, `refreshSession()` calls `GET /auth/session` to validate it. If the API rejects it, `clearSession()` runs.

### Sign-Out Flow

1. `signOutCurrentUser()` → `POST /auth/sign-out` (deletes server-side session) → `clearSession()` (clears localStorage + sets state to `{data: null}`)
2. `reloadSignedOutRoute('/auth/sign-in')` → `window.location.assign('/auth/sign-in')`
3. Backend: `authSignOut` deletes row from `auth_sessions`, clears `komuna_session` cookie

## Protected Route Pattern

Any route that requires authentication **must** check `authClient.useSession()` before rendering protected content:

```tsx
import { Navigate } from 'react-router-dom'
import { authClient } from '../../lib/auth'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const session = authClient.useSession()

  if (session.isPending) {
    return <main style={{ padding: 32 }}>Loading session...</main>
  }

  if (!session.data) {
    return <Navigate to="/auth/sign-in" replace />
  }

  return <>{children}</>
}
```

## Routes That Need Auth Guards

### ✅ Protected (has auth guard)

- `WorkspaceRoute` (`/programs/:id/admin`, `/programs/:id/manage`, `/programs/:id/member`) — fixed 2025-07-03
- `/dashboard/programs/...` — wraps `WorkspaceRoute`
- `PlatformRoute` (`/platform`) — checks `workspace.isSuperAdmin` but relies on `useWorkspace()` fetch failure; could still briefly flash for unauthenticated users

### ❌ Missing auth guard (vulnerable to stale-render after sign-out)

- `/wallet` — `WalletPage` — calls `apiClient.get('/wallet')` without auth check; will error but won't redirect
- `/my/bookings` — `BookingsPage` — same pattern
- `/profile` — `ProfilePage` — imports `authClient` but doesn't guard the route
- `/notifications` — `NotificationsPage`
- `/settings/notifications` — `NotificationSettingsPage`

These pages show their error states when unauthenticated instead of redirecting to sign-in.

## The "??" and "User" Bug

**Symptom:** After sign-out, pressing back loads a dashboard URL. Top bar shows `'??'` avatar and `'User'` name instead of real user info.

**Root cause:** `WorkspaceRoute` (pre-fix) rendered `DashboardShell` unconditionally — no auth check. `ProfileMenu` inside `DashboardShell` calls `authClient.useSession()` which returns `{data: null}` because localStorage was cleared by sign-out. Falls back to `getInitials(null) = '??'` and `displayName = 'User'`.

**Fix:** Added `authClient.useSession()` check to `WorkspaceRoute` with redirect to `/auth/sign-in` when session is null (commit `61bb560`).

## Verification

```bash
# Confirm the built JS checks useSession before rendering dashboard
curl -s "https://komuna.ahsanworks.com/assets/$(curl -s https://komuna.ahsanworks.com/ | grep -oP 'assets/index-[^\"]+\.js')" | grep -c 'useSession'
# Should return 2+ (one in WorkspaceRoute, one in ProfileMenu/TopNav)
```
