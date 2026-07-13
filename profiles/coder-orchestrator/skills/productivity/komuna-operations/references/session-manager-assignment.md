# Session Manager Assignment

Session learning from implementing assigned manager/coach selection for Komuna session activation.

## Data/API pattern

- Persist the selected coach/manager on the `sessions` row as a product-manager program-member reference (for example `assigned_manager_id`).
- Keep the legacy `coach` text field as a display fallback, but prefer the joined manager name when `assigned_manager_id` is present.
- All session-returning API shapes should include both snake/camel compatibility fields used by the frontend, e.g. `assigned_manager_id`, `managerId`, `managerName`, and `managerImageUrl`.
- For pages that fetch active session instances (cards/bookings/product sessions), join through `program_members -> users/auth_users` so coach name and profile picture are available wherever sessions are displayed.

## Activation guard pattern

- Do not activate a session without an assigned valid product manager.
- Accept a manager id in the activation payload (`managerId` and/or `assigned_manager_id` for compatibility).
- Validate that the manager is assigned to the same product via `product_managers(product_id, program_member_id)` before updating the session.
- On success, set `is_active=1`, `status='scheduled'`, `assigned_manager_id=<manager>`, and update the display `coach` fallback to the selected manager name.
- Return the full `sessionDTO` after activation so the UI refresh can immediately display manager metadata.

## Admin Sessions UI pattern

- If activation is requested and no manager is selected, open a modal instead of activating.
- The picker should be single-select only, searchable, scrollable, and able to reveal more managers as the user scrolls.
- Use product-scoped managers from `/programs/:id/members` filtered by `role === 'manager'` and matching `product_id`.
- Show manager profile image/avatar beside the name in both the picker and compact session rows.

## Verification checklist

- `go test ./...` from `/home/ubuntu/projects/komuna/api/v1`.
- `go build` the API binary and restart `komuna-api.service`.
- `npm run build` from `apps/web`.
- Verify API health/ready endpoints and confirm `assigned_manager_id` exists in SQLite after service restart.
- Deploy frontend `dist/` to `/var/www/html/projects/komuna/` and verify `https://komuna.ahsanworks.com/` returns the new built JS bundle.
