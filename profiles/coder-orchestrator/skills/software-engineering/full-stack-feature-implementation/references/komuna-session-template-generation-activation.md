# Komuna session template generation + activation

Use when implementing Komuna recurring/session-template workflows in the local Go + SQLite + Vite stack.

## Durable pattern

- Treat `session_templates` as blueprints only. They are never bookable; bookings/claims attach to generated `sessions` rows.
- Keep generation and activation separate:
  - template save/edit: admin-only;
  - generation from existing template: admins or product-scoped managers;
  - generated sessions: `is_active=0` by default;
  - activation/deactivation: admins or assigned product managers.
- Template edits affect future generation only. Do not mutate existing generated sessions when a template changes.
- Add a `template_id` FK/column on generated sessions and a unique index on `(template_id,start_time)` to make generation idempotent and skip duplicate dates.
- Template time data must be explicit and previewable: weekday, start time, end time/duration, and generated date/time in the UI.
- Frontend should expose two clear surfaces:
  - admin template CRUD/generation page;
  - activation page that filters by date/product and uses mobile cards rather than wide tables.

## Backend pitfalls

- Route ordering matters in `programTree`: `/programs/:id/sessions/activate` must be handled before falling back to normal `programSessions`.
- Existing global `/sessions/:id/activate|deactivate` endpoints may be permissive; add an authorization guard that resolves `session -> product -> program` and checks admin/product-manager rights before toggling `is_active`.
- In this repo, schema additions are often additive strings in `schema()`. Create `session_templates` before an `ALTER TABLE sessions ADD COLUMN template_id REFERENCES session_templates(id)` to avoid startup migration surprises.
- Go grouped struct tags like `FromDate, ToDate string \`json:"from_date"\`` give both fields the same JSON key. Use separate fields/tags for `from_date` and `to_date`.
- If the Go package has unrelated compile failures from other in-progress files, do not deploy/restart the API with partial feature changes. Report the blocker and keep frontend build verification separate.

## Frontend/mobile checklist

- Use card stacks for mobile activation lists, not tables.
- Date/product filters should remain reachable near the top.
- Activation/deactivation buttons should become full-width on narrow screens.
- Deactivation modal needs a required reason and must fit within the viewport.
