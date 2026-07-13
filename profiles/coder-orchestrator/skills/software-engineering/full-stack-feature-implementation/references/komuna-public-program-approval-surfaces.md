# Komuna public-program approval surface cleanup

When public vs private/need-approval programs differ only by member join approval, keep the change scoped to member join-request surfaces, not all operational approvals.

## Pattern

1. Identify the active Komuna local stack paths:
   - Frontend admin approvals page: `apps/web/src/pages/ApprovalsPage.tsx`
   - Admin management dashboard: `apps/web/src/pages/AdminDashboardPage.tsx`
   - Admin dashboard DTO: `apps/web/src/lib/api-types.ts`
   - Go admin dashboard API: `api/v1/dashboard_handlers.go`
2. For public programs:
   - Do not fetch `/programs/:id/join-requests`.
   - Hide the Join requests stat/tab/section on the Approvals page.
   - Default the Approvals page to booking requests if it is still reachable.
   - Hide the Approvals tile/button and `Review now` CTA from the Management page if the product direction is that public programs should not expose that page entry point.
3. Add `program_visibility` to dashboard summary responses when a dashboard component needs to hide/show UI based on visibility; do not infer from counts alone.
4. Keep need-approval/private behavior unchanged.

## Verification

- Frontend targeted tests for the affected pages, e.g. `npm run test -- ApprovalsPage.test.tsx AdminDashboardPage.test.tsx` or separate runs.
- Vite production build with Komuna auth-env safety: `env -u VITE_NEON_AUTH_URL npm run build`.
- Go API test from module dir: `cd api/v1 && go test ./...`.
- Deploy both sides when DTO/API changes:
  - `go build -o /home/ubuntu/projects/komuna/api/server .` from `api/v1`, then `sudo systemctl restart komuna-api`.
  - `rsync` web `dist/` to `/var/www/html/projects/komuna/`.
- Smoke the local API with a dev header if the route is auth-gated, e.g. `X-Komuna-User: user-demo`, and confirm `program_visibility` is present.

## Pitfalls

- Removing join approvals is not the same as removing booking approvals; preserve booking-request flows unless the user explicitly asks to remove the whole approvals entry point.
- The management page may have multiple entry points: a stat-card CTA (`Review now`) and a nav tile (`Approvals`). Hide both for public programs when requested.
- If backend DTO fields change, frontend-only deployment is not enough; rebuild/restart the Go service too.
