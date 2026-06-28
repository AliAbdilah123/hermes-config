# Komuna source-of-truth correction after local-stack migration

Use this when migrating Komuna from the cloned upstream repo to the local Go + SQLite + Vite deployment stack.

## Lesson

The cloned Komuna repo (`apps/web`) is the source of truth for product/UI behavior. Do **not** replace the frontend with a simplified donor UI from `komuna-old` just because `komuna-old` already has a working Go/SQLite stack. The stack migration should preserve the upstream application and port only the runtime/backend/deployment seams needed for local hosting.

## Corrective workflow

1. Before deploying, compare the migrated tree against the freshly cloned source:
   - Suspect any new top-level `frontend/` copied from `komuna-old`.
   - Verify deployed build assets come from `apps/web/dist`, not `frontend/dist`.
   - Search deployed JS for `komuna-old`; it should not appear.
2. Keep the real frontend in `apps/web` and apply only local deployment seams:
   - Set Vite `base: '/projects/komuna/'`.
   - Build with `VITE_API_BASE_URL=/projects/komuna/api/v1` or another correct same-deployment base.
   - Sync `apps/web/dist/` to `/var/www/html/projects/komuna/`.
3. Keep the isolated local backend in `api/`, but adapt its routes to the upstream frontend contract incrementally rather than replacing the frontend:
   - Start with `/api/v1/programs` for discovery.
   - Add notification endpoints needed by top nav (`/api/v1/notifications`, `/api/v1/notifications/unread-count`).
   - Continue adding endpoint shims/domain handlers as pages are exercised.
4. Verify by behavior and source markers, not just a green build:
   - `go test ./...` and `go build -o server .` from `api/`.
   - `npm run build` from `apps/web`.
   - Public `curl` for `/projects/komuna/` and `/projects/komuna/api/v1/programs`.
   - Inspect deployed JS for upstream markers such as `available-programs` or `dashboard-redesign-preview`, and absence of `komuna-old`.
5. If `npm run lint` fails on pre-existing upstream lint debt, report that separately from migration/deployment success. Do not rewrite the frontend to satisfy lint unless the user asked for lint cleanup.

## Pitfall

A working public page is not proof of a correct migration. If the page looks like `komuna-old`, the migration likely copied the donor UI. Restore the frontend source of truth to `apps/web` and port backend/API seams instead.