# Manual recovery of missed social-inbox messages

Use this pattern when an established webhook-driven inbox needs a user-triggered recovery action for messages the webhook did not capture.

## Feasibility gate

Before designing the recovery worker, prove with the real provider account and current API version that the app can:

- list the receiving account's conversations;
- identify the conversation for the verified sender's stable provider ID;
- retrieve stable message IDs, sender/recipient IDs, provider timestamps, text, supported attachment references, and pagination cursors;
- distinguish inbound messages from echoes/outbound messages;
- page far enough back to find a known locally captured boundary;
- use the configured token type/scopes under the app's current review/mode;
- understand provider retention/history limits.

Save only redacted response-shape fixtures. If the provider cannot expose history, disable recovery for that platform and state the limitation; never simulate completeness.

## Minimal durable design

Prefer one normalized staging table shared by supported providers:

- social identity ID;
- platform;
- external message ID with a platform-scoped unique constraint;
- provider-sent timestamp;
- sender and recipient stable IDs;
- text and normalized attachment-reference JSON;
- status (`pending`, `processing`, `failed`), attempt count, and bounded error code.

Index by `(social_identity_id, status, provider_sent_at, external_message_id)`.

Fetch provider pages into durable staging before draining. Process in strict `(provider_sent_at ASC, external_message_id ASC)` order. Call the same idempotent domain processor used by webhooks; do not create a second note-creation path. Delete a staged row only after processing commits. On the first failure, retain that row, stop the identity's drain, and retry it before newer rows.

Derive the initial lower boundary from the latest successfully captured external message when the provider API permits. Do not add a cursor table preemptively; add one only if real pagination behavior proves the captured-message boundary unreliable or inefficient.

## Concurrency and privacy

- The trigger endpoint is authenticated, CSRF-protected, owner-scoped, and active-identity-only.
- Serialize sync per social identity with a durable database claim; reject or report concurrent attempts.
- Fetch and stage only messages whose sender, recipient, and receiving account match the selected verified identity/integration.
- Return counts and completeness metadata, not message bodies, raw provider payloads, tokens, or personal identifiers.
- Keep raw provider payloads out of storage when normalized processor inputs suffice.
- Preserve reference-only media ingestion; recovery must not eagerly download external media.

## Completeness contract

A useful response separates:

- fetched;
- processed;
- duplicates;
- remaining;
- whether the known local boundary was reached;
- provider's oldest available timestamp when history is truncated.

`complete=true` means the known boundary was reached and every staged row through the provider's latest page was processed. Provider retention, page caps, or a missing boundary require `complete=false` with a clear user-facing explanation.

## Required checks

- out-of-order fetched pages still drain oldest-first;
- equal timestamps use external message ID as deterministic tie-breaker;
- webhook delivery between fetch and drain creates exactly one record;
- repeated manual recovery is idempotent;
- failure of the oldest staged row blocks newer rows and survives restart;
- cross-user identity IDs reveal no ownership information;
- wrong sender/recipient, echoes, malformed payloads, timeouts, and non-2xx provider responses fail closed;
- Settings exposes one independently busy action per active platform identity with an accessible live status;
- public authenticated E2E creates a known gap, recovers it, reloads, and reruns with zero new records.

## Scaling boundary

Start with bounded synchronous pages/messages and HTTP timeouts. Introduce a background job only when measured recovery gaps exceed the request budget; do not build queue infrastructure merely because the operation contains a loop.
