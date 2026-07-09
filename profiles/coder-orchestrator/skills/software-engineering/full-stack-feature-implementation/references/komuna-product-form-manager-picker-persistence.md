# Komuna product forms: manager picker + persistence verification

Use when implementing or fixing Komuna admin product create/edit forms, especially product-manager assignment, blank-saved fields, or scalable member selection.

## Lessons

- Do not render all program members as a checkbox wall in the product form. Use a compact selected-manager chip area plus an `Add manager` modal.
- For the first pass, avoid new dependencies and avoid backend pagination until measured necessary: fetch active members once, search client-side, and lazy-render visible rows in chunks (for example 12 at a time with `Load 12 more`).
- Keep selected managers pinned/visible as chips outside the search results so admins can see who will manage the product before saving.
- Product create/edit should confirm after validation and before mutation: `Create this product?` or `Save product changes?`, then run the existing save path with a pending/loading state.
- Keep the payload field stable (`managerIds`) and the backend response field stable (`manager_ids`) unless doing a planned API migration.

## Field persistence pitfall

A passing frontend build does not prove form fields persist. For product create/edit, verify every visible form field reaches the database or related table:

- `products`: `name`, `description`, `type`, `capacity`, `booking_window_days`, `max_validity_extension_date`, `cancellation_tiers`, `status`.
- `custom_fields`: custom field name + required flag.
- `session_templates.weekly_slots`: weekly schedule JSON.
- `product_managers` + `program_member_roles`: manager assignments.

Watch for frontend camelCase vs backend snake_case. Accept both when needed at the API boundary, e.g. `bookingWindowDays` and `booking_window_days`.

## Minimal test pattern

Add one backend test that creates a product, edits it, then queries the DB directly for the persisted fields. This catches fields that display in React but silently save blank.

Use direct DB assertions for related tables rather than only checking JSON response shape.

## UX acceptance checklist

- Form never displays every active member at once.
- Admin can search member name/email.
- Results are chunked/lazy-rendered with a load-more action.
- Selected managers remain visible even when search changes.
- Submit validates at least one manager and nonblank custom fields.
- Submit opens a confirmation CTA before create/update mutation.
- Backend tests prove create and edit persist visible form fields.
