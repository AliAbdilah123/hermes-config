# Session Template Generation + Activation Design Notes

Use this when planning or implementing Komuna session-template generation and the separate activation workflow.

## Confirmed product decisions

- Session templates are blueprints only; members cannot book templates directly.
- Template creation/editing is Program Admin only.
- Product Managers may generate concrete sessions from existing templates for products they are assigned to.
- Generation range defaults to 4 weeks and is capped at 12 weeks.
- Generated sessions must never auto-activate. They are created as scheduled/inactive and require separate activation.
- Template edits apply to future generation only; existing generated sessions do not move automatically.
- One-off sessions should live in the same sessions area but be clearly labeled as not template-backed.
- Template time setup is required: start time and end time in the program timezone.
- Generation preview must show exact date, start time, end time, and timezone for every generated session before confirmation.

## Spec alignment

The Komuna spec says:
- Sessions are generated from a weekly template plus one-off additions.
- Active state is per date/session, not a persistent template flag.
- By default, no sessions are active on any given day.
- Assigned managers or program admins activate a session for it to run.
- Outside booking window requires approval unless the session is activated.
- Deactivation requires a reason and triggers cancellation/compensation + notifications.

## UX expectations

Template page:
- Route suggestion: `/programs/:id/admin/session-templates`.
- Template list grouped by session-type product.
- Admin-only create/edit drawer with product, name, weekdays, required start/end time, assigned managers, optional location/room, enabled flag.
- Generate action usable by admin or assigned product manager.
- Preview shows generated sessions and skipped duplicates.

Activation page:
- Admin route suggestion: `/programs/:id/admin/sessions/activate`.
- Manager route suggestion: `/programs/:id/manage/products/:productId/activate`.
- Daily/weekly operations board with date picker, filters, status, capacity/taken, booking state, and activation actions.
- Activation is one click and notifies booked members.
- Deactivation requires reason, shows affected members, and triggers cancellation/compensation.

Mobile requirements:
- Use stacked cards instead of wide tables below tablet width.
- Keep date picker and filters reachable at top.
- Make Activate/Deactivate actions full-width on phones.
- Deactivation reason modal must fit phone screens; affected members list should scroll inside modal.
- Generation preview should show one generated session per card with date/time/timezone visible.
- Avoid horizontal scrolling.

## Data shape guidance

Minimal v1 shape:
- `session_templates`: `id`, `program_id`, `product_id`, `name`, `weekdays`, `start_time_local`, `end_time_local`, `manager_ids`, timezone snapshot, `is_enabled`, `created_by`, timestamps.
- `sessions.template_id`: nullable source-template link.
- Duplicate prevention should be based on `(template_id, start_time)` or equivalent unique guard.
- Generated sessions should be `status='scheduled'` and `is_active=false`.

Keep capacity inherited from product for v1; per-session capacity override is future/out of scope unless explicitly requested.
