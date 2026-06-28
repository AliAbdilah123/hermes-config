# Komuna basic sign-up role and landing redirect

Use when fixing Komuna local-stack auth behavior for newly-created/basic users.

## Intended behavior

- A newly signed-up user is a basic authenticated user only.
- Do **not** synthesize program roles (`member`, `manager`, `admin`) for authenticated users with no matching `State.Members` entry.
- Do **not** mark newly signed-up users as `isSuperAdmin`.
- After sign-up, default redirect should be the landing/discovery page (`/`), not `/dashboard` / workspace chooser.
- If a no-workspace basic user reaches `/dashboard`, redirect them back to `/` rather than showing the workspace picker/no-workspace page.
- Pending program memberships may still show the pending-access explanation.

## Backend pattern

In the Go+SQLite API (`api/v1/main.go`), keep the demo/admin fallback distinct from real authenticated sessions:

1. Determine whether the request is from a real auth session (`userFromRequest`) or explicit dev header (`X-Komuna-User`).
2. Only use the seeded demo admin workspace fallback when there is no authenticated session and no explicit dev user.
3. Return `isSuperAdmin: false` and `programs: []` for authenticated users with no program memberships.

Regression test shape:

1. Create a temp SQLite DB via `t.Setenv("SQLITE_DB_PATH", filepath.Join(t.TempDir(), "komuna-test.db"))`.
2. POST `/api/v1/auth/sign-up` with email/password/name.
3. GET `/api/v1/me/workspace` with `Authorization: Bearer <token>`.
4. Assert `isSuperAdmin == false` and `len(programs) == 0`.

## Frontend pattern

- In `AuthPage`, compute default redirect as:
  - sign-up: `/`
  - sign-in: `/dashboard`
  - preserve a safe same-origin `redirectTo` if present.
- In `DashboardEntryPage`, when there are no manageable choices and no pending memberships, return `<Navigate to="/" replace />`.
- Keep pending memberships on the pending/no-access explanatory state.

Regression test shape:

- `AuthPage.test.tsx`: authenticated `/auth/sign-up` with no `redirectTo` lands on a route marker for `/`, not `/dashboard`.
- `DashboardEntryPage.test.tsx`: workspace `{ isSuperAdmin:false, programs:[] }` redirects to `/` and does not render `dashboard-entry-empty`.

## Deployment verification

- Run targeted frontend tests for `AuthPage` and `DashboardEntryPage`, then `npm run build`.
- Deploy the Vite `dist/` to the actual nginx-served app path (for Komuna: `/var/www/html/projects/komuna/`).
- Curl the public index and referenced JS/CSS assets to confirm new hashes return 200.
- Public API smoke: create a throwaway user, fetch `/me/workspace`, confirm no super-admin/program role.
