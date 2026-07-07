# Session Template Generation + Activation Design

Captured from a Komuna design-planning session. Use this as domain guidance when planning or implementing session templates and activation; still verify against the live product spec and code before changing behavior.

## Confirmed product decisions

- **Template create/edit:** Program Admins only.
- **Session generation from templates:** Program Admins can generate for any program product; Product Managers can generate for assigned products only.
- **Generation range:** default 4 weeks, max 12 weeks.
- **Auto-activation:** never. Generated sessions must start inactive.
- **Template edits:** future generation only; do not mutate already generated sessions automatically.
- **One-off sessions:** allowed in the same sessions/admin area, but visually and technically separate from template-backed sessions.

## Spec-aligned mental model

| Concept | Purpose | Bookable? |
| --- | --- | --- |
| Session Template | Weekly schedule blueprint: product, weekday(s), local start/end time, manager assignment defaults. | No |
| Generated Session | Concrete dated instance created from a template or one-off action. | Yes |
| Activation | Per-date operational confirmation that a generated session will run. | Enables direct out-of-window booking |

Important: activation belongs to the generated `sessions` row/date, not the `session_templates` row.

## Recommended UX split

### Admin template page

Suggested route: `/programs/:id/admin/session-templates`

- Template list grouped by session-type product.
- Admin-only create/edit drawer.
- Generate sessions action with preview.
- `Add one-off session` action in the same area, clearly labeled as non-template-backed.

Template fields:
- session-type product only
- name
- weekday(s)
- local start/end time in program timezone
- assigned manager(s)
- optional location/room if needed
- enabled/disabled for future generation only

Generation flow:
1. Actor chooses template and date range.
2. Default range is 4 weeks; max is 12 weeks.
3. Preview exact generated dates/times.
4. Warn about duplicate/skipped sessions.
5. Create real `sessions` rows with `status='scheduled'` and `is_active=false`.

### Separate activation page

Suggested routes:
- Admin: `/programs/:id/admin/sessions/activate`
- Manager: `/programs/:id/manage/products/:productId/activate`

Operations-board behavior:
- Date picker defaults to today.
- Filters: product, manager, active/inactive, has bookings.
- Rows/cards show time, product, assigned managers, capacity/taken, booking-window state, active status, booked member count.
- Activate: one-click per generated session/date; notify booked members and audit `session.activated`.
- Deactivate: require reason, show affected bookings, trigger cancellation/compensation, notify members/admin/managers, audit `session.deactivated`.

## Data model notes

Minimal v1 shape:

`session_templates`
- `id`
- `program_id`
- `product_id`
- `name`
- `weekdays` JSON/text
- `start_time_local`
- `end_time_local`
- `manager_ids` JSON/text
- `timezone` snapshot from program
- `is_enabled`
- `created_by`
- `created_at`
- `updated_at`

`sessions`
- keep existing fields
- add nullable `template_id` if absent
- duplicate prevention should be based on `(template_id, start_time)`

Avoid adding session-level capacity override unless explicitly requested; the spec treats it as future scope.
