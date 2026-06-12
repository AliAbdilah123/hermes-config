# Business CRM Import + Inbox MVP Delivery Notes

Use these notes when extending an existing React/Vite + Go + SQLite business/CRM app with data import, template messaging, inbox, and external messaging-worker integration.

## Durable patterns

- Keep CSV sample format server-owned. Add a backend `.../import/sample` endpoint and have the frontend download from it instead of duplicating headers in client code; this prevents frontend/backend schema drift.
- CSV import should report `total`, `inserted`, `updated`, `duplicates`, and row-level `errors` so users can safely replace seed/mock data with real business data.
- For business/contact data, model contacts independently and use a many-to-many join table between businesses and contacts. Imports can create/link a primary contact from columns such as `contact_name`, `contact_phone`, `contact_email`.
- For script/message templates, support dotted placeholders (`{{business.name}}`, `{{business.city}}`, `{{contact.name}}`) rather than only flat placeholders. Render through a server/API path or a shared renderer so bulk send and preview use the same substitutions.
- For real-time/external integrations that need another runtime (e.g. Baileys for WhatsApp in Node beside a Go API), keep the Go API as source of truth and add a worker boundary. Until credentials/session are configured, return honest `mock`/`queued`/`not_connected` states and persist the queued attempt instead of faking success.
- When persisting inbox/conversation rows that may not yet be associated with a business/contact, use nullable foreign keys, not zero IDs. In Go/SQLite inserts, convert `0` to `nil` before writing FK columns to avoid FK errors/panics and keep general inbox messages representable.
- Bulk actions such as archive, add-to-CRM, and send-message should call bulk endpoints with selected IDs and clear status reporting. Disable or guard potentially destructive/broadcast actions when selection is empty.

## UI delivery checklist

- Business database: full-width/full-height table, working search/filter/sort, bulk select, bulk archive/add-to-CRM/send actions, sample CSV download, import result summary.
- Business detail: make names clickable from lists/tables and show short business/contact/qualification data in a modal or detail view.
- Scripts page: show templates in a table; edit via modal with a textarea; preview/render with representative business/contact data.
- CRM kanban: make the board the primary/fullscreen content; replace persistent quick-add forms with an `Add business` button/modal; support drag/drop stage changes plus business detail/comment modal.
- Inbox: show honest connection status; if the worker is not configured, keep send attempts queued/mock and visible in conversations.
- Layout: make desktop sidebar collapsible without breaking mobile navigation.

## Verification checklist

- `go test ./...` and production Go build pass.
- `npm run build` passes and deployed `dist/` is served by nginx.
- Worker scaffold syntax/check command passes if a sidecar runtime is added.
- Smoke test with real API calls: login/session if applicable, sample CSV download, CSV import, business search/detail, contact association, template render, CRM stage update, messaging status, queued send, conversations list.
- Check service logs after messaging smoke tests for panics; a 200/queued API response is not enough if the service panicked asynchronously.
- Final report should distinguish real connected sends from mock/queued sends and state what remains to configure for live messaging.