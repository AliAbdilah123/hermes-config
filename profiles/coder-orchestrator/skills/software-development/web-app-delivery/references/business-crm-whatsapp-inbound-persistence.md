# Business CRM WhatsApp inbound persistence

Session pattern from `local-business-os-indonesia` / Bisnis Lokal WhatsApp inbox.

## Problem shape
- Baileys worker logs `messages.upsert` inbound messages, but the app inbox stays empty.
- Existing app may already support outbound sends, QR pairing, `/whatsapp/status`, and DB tables for `whatsapp_conversations` / `whatsapp_messages`.
- The missing link is often not Baileys reception; it is worker-to-API webhook configuration and backend persistence.

## End-to-end fix pattern
1. **Worker payload**
   - On `messages.upsert`, skip `msg.key.fromMe`.
   - Normalize payload fields:
     - `type: "whatsapp.message.received"`
     - `id: msg.key.id`
     - `from: msg.key.remoteJid`
     - `display_name: msg.pushName || ''`
     - `text`: conversation text, extended text, image caption, video caption, or empty.
     - `raw`: original Baileys message for fallback parsing.
   - POST to `WHATSAPP_WEBHOOK_URL` and log non-2xx responses, not only network failures.

2. **Backend webhook**
   - Add a server-side webhook route such as `/api/v1/whatsapp/webhook` that does not require browser auth cookies/CSRF when the worker calls it locally.
   - Keep it internal/localhost by deployment config unless a shared-secret/signature gate is added.
   - Accept normalized fields and optionally parse `raw` fallback values.
   - Require `from`; convert empty text to a clear placeholder like `[non-text WhatsApp message]`.

3. **Persistence**
   - Ensure or create a conversation by `wa_id` for inbound-only contacts/groups.
   - Save message with `direction='inbound'`, `status='received'`, and `provider_message_id`.
   - Add idempotency: unique partial index on `provider_message_id` and return existing row for duplicate webhook delivery.
   - For deployed SQLite DBs, add best-effort `ALTER TABLE` migrations for new columns (`wa_id`, `display_name`, `provider_message_id`) before relying on them.

4. **Listing API**
   - Conversation list should include latest message fields: body, direction, timestamp, display/display name, `wa_id`.
   - Messages endpoint should return persisted inbound messages by conversation id.

5. **Frontend inbox**
   - Poll conversations and selected conversation messages while the WhatsApp page is open.
   - Render `direction === 'inbound'` as contact bubbles and `direction === 'outbound'` as self bubbles.
   - When replying to an inbound-only conversation, send to `active.wa_id` before falling back to `active.phone` or selected business phone.

6. **Deployment verification**
   - Confirm systemd/API service has `WHATSAPP_WORKER_URL` set.
   - Confirm worker service has `WHATSAPP_WEBHOOK_URL=http://127.0.0.1:<api-port>/api/v1/whatsapp/webhook` (or equivalent internal URL).
   - Restart both services after binary/worker/config updates.
   - Smoke test with a synthetic webhook POST, then fetch the nginx-proxied conversations endpoint with an authenticated cookie and confirm latest conversation has `last_direction: inbound` and non-empty `last`.

## Commands used in this session
```bash
go test ./...
npm run build
curl -fsS -X POST http://127.0.0.1:<api-port>/api/v1/whatsapp/webhook \
  -H 'content-type: application/json' \
  -d '{"type":"whatsapp.message.received","id":"SMOKE-...","from":"628111222333@s.whatsapp.net","display_name":"Smoke Test WA","text":"Halo smoke inbound"}'
```

## Pitfalls
- A worker can be connected and logging inbound messages while the app remains empty because `WHATSAPP_WEBHOOK_URL` is blank.
- Outbound-only conversations often have business/contact IDs but no `wa_id`; inbound-only conversations often have `wa_id` but no business/contact IDs. Both shapes must list cleanly.
- Do not write zero IDs into nullable foreign keys; use NULL for absent business/contact/conversation links.
- If the webhook is exposed publicly without auth, anyone can insert inbox rows. Keep it localhost/internal or add a shared secret.
