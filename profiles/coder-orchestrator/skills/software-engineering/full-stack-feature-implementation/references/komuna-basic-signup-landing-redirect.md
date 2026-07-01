# Komuna basic sign-up role and landing redirect

Use when fixing Komuna local-stack auth behavior for newly-created/basic users.

## Intended behavior

- A newly signed-up user is a basic authenticated user only.
- Do **not** synthesize program roles (`member`, `manager`, `admin`) for authenticated users with no matching `State.Members` entry.
- Do **not** mark newly signed-up users as `isSuperAdmin`.
- After sign-up, default redirect should be the landing/discovery page (`/`), not `/dashboard` / workspace chooser.
- If a no-workspace basic user reaches `/dashboard`, redirect them back to `/` rather than showing the workspace picker/no-workspace page.
- Basic members with pending program memberships are also redirected to `/` — the pending-access explanation page is only for users who have pending admin/manager roles (checked via `manageableRoleFor(program)` on pending programs).

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
- In `DashboardEntryPage`, when there are no manageable choices, check pending programs for admin/manager roles via `manageableRoleFor(program)`. If none have manageable roles, return `<Navigate to="/" replace />` — this covers both no-workspace users and basic members with pending memberships. Only show the pending-access explanation page when a pending program has an admin or manager role.

Regression test shape:

- `AuthPage.test.tsx`: authenticated `/auth/sign-up` with no `redirectTo` lands on a route marker for `/`, not `/dashboard`.
- `DashboardEntryPage.test.tsx`: workspace `{ isSuperAdmin:false, programs:[] }` redirects to `/` and does not render `dashboard-entry-empty`.
- `DashboardEntryPage.test.tsx`: workspace with a pending program membership where the role is `member` (not admin/manager) also redirects to `/` and does not render `dashboard-entry-empty`.
- `DashboardEntryPage.test.tsx`: workspace with a pending program membership where the role is `admin` or `manager` renders `dashboard-entry-empty` with the pending approval heading.

## Deployment verification

- Run targeted frontend tests for `AuthPage` and `DashboardEntryPage`, then `npm run build`.
- Run backend regression tests and build from `api/v1` (`go test ./...`, `go build -o server .`).
- Komuna's systemd unit may execute `/home/ubuntu/projects/komuna/api/server` while the local build artifact is `api/v1/server`; inspect `systemctl show komuna-api.service -p ExecStart -p EnvironmentFiles -p ActiveState`, then install/copy the rebuilt binary to the actual `ExecStart` path before restarting.
- Deploy the Vite `dist/` to the actual nginx-served app path (for Komuna: `/var/www/html/projects/komuna/`).
- Curl the public index and referenced JS/CSS assets to confirm new hashes return 200.
- Public API smoke through nginx uses the subpath API base `http://168.110.213.104/projects/komuna/api/v1`, not host-root `/api/v1`: create a throwaway user, fetch `/me/workspace` with its bearer token, confirm no super-admin/program role.
