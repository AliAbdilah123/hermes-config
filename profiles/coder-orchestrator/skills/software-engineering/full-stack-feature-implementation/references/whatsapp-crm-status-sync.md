# WhatsApp actions should drive CRM status

Use this reference when a local Go/SQLite + React/Vite business CRM has WhatsApp sending plus CRM pipeline/status fields.

## Product rule

When the user sends a WhatsApp message to a selected business/prospect, the app should treat that business as contacted. Messaging is not just a communication log; it is a CRM event.

## Backend pattern

1. Ensure the WhatsApp send payload includes `business_id` when the message is tied to a business.
2. Persist the outbound WhatsApp message first as `queued`.
3. Mark the business as contacted for early-stage statuses only:
   - `prospect`
   - `qualified`
   - `lead`
   - empty status
4. Update the latest CRM lead for that business:
   - `Lead` or `Qualified` -> `Contacted`
   - keep later stages like `Meeting`, `Proposal`, `Won`, `Lost` unchanged
5. If the business has no CRM lead yet, create one with:
   - channel: `WhatsApp`
   - stage: `Contacted`
   - next action: `Follow up WhatsApp reply`
6. Return a response flag such as `crm_status_updated` so the frontend can refresh or optimistically update UI state.
7. If the WhatsApp worker/provider is offline or returns non-2xx, keep the message queued and still apply the CRM status transition; return HTTP 202 with worker error metadata rather than failing the whole CRM action.
8. Apply the same CRM transition in bulk template-send paths, not only the one-off `/whatsapp/send` endpoint.

## Test cases to add first

- Sending a WhatsApp message for a qualified business updates `businesses.status` to `contacted` and latest `leads.stage` to `Contacted`.
- Sending a WhatsApp message for a business with no lead creates a `Contacted` lead.
- Worker/provider failure still returns accepted/queued and still updates CRM status.
- Later-stage leads are not regressed back to `Contacted`.
- Tenant scoping prevents updating another tenant's business/lead.

## Frontend pattern

- Pass `business_id` from the selected business when calling `/api/v1/whatsapp/send`.
- If response includes `crm_status_updated`, refresh businesses/leads or update selected business status locally to `contacted`.
- Keep the sent message visible in the chat even if provider delivery is queued/offline, but surface provider error separately if available.
