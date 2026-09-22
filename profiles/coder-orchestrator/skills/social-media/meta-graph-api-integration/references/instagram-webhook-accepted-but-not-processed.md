# Instagram webhook returns 200 but messages are not processed

Use this when Meta successfully verifies the callback and Nginx shows signed `POST` requests returning `200`, but no note, identity activation, or other domain record appears.

## Key distinction

An HTTP `200` proves only that the webhook transport accepted the delivery. It does **not** prove that the application recognized or persisted any event inside the payload. Many webhook handlers intentionally return `200` for ignored/unmatched events to prevent retries.

## Boundary-by-boundary diagnosis

1. **Provider → edge:** Confirm a provider user agent reached the exact callback route. Separate Meta deliveries from manual `curl` probes.
2. **Edge → handler:** Confirm status and timestamp. A successful verification `GET` is independent of event `POST` delivery.
3. **Signature → parser:** Establish that signature validation and JSON parsing succeeded without logging raw payloads, tokens, signatures, or message text.
4. **Parser → domain logic:** Inspect all silent-ignore predicates: echo, missing text/MID/sender/recipient, self-event, unsupported event shape, or recipient mismatch.
5. **Domain logic → storage:** Query the durable records expected from the event. Do not infer success from HTTP status alone.

## Instagram account-ID namespace pitfall

Never assume a manually copied configured account ID matches the ID emitted in webhook `recipient.id` or usable with a particular Instagram User token. For every configured token, query its own identity context:

```http
GET https://graph.instagram.com/{version}/me?fields=id,username,account_type
Authorization: Bearer <that token>
```

Compare the returned `id` with:

- the configured dedicated receiver ID;
- the active integration record in the database;
- webhook recipient filtering;
- polling/outbound URL construction.

Update each account ID only from its corresponding token. Do not copy IDs between tokens/accounts or mix Facebook Page IDs, Instagram business IDs, and Instagram-scoped messaging IDs.

A common silent-loss pattern is:

```text
Meta POST → signature valid → HTTP 200 → recipient ID not recognized → unmatched/ignored → no DB row
```

## Safe correction and verification

1. Back up the environment file and runtime database.
2. Derive each account ID independently via that token's `/me`.
3. Update only the associated ID fields.
4. Restart the service that reads the environment file.
5. Verify the running service is healthy and the active integration DB record contains the token-derived receiver ID.
6. Send one unique, fresh, text-only DM.
7. Correlate its timestamp across Nginx access logs, application diagnostics, and the resulting DB record.
8. Declare READY only after the real authenticated message is persisted/processed as expected.

## Dedicated inbox fallback ownership

When unmatched inbound DMs should still become notes, the fallback owner must belong to the **receiver integration**, not the sender:

```text
webhook recipient.id
→ active dedicated integration.instagram_user_id
→ integration.owner_user_id
→ notes.user_id
```

Rules:

- First let the normal identity flow match an active sender and save under that identity's owner.
- Only `unmatched` falls back to the dedicated integration owner.
- Do not hardcode sender usernames or add them to env/seed data.
- Add a nullable owner foreign key to the integration record when the schema lacks ownership. Use an existing owner email only as a one-time startup/backfill bridge; delivery-time lookup must use recipient account ID.
- If no owner is associated, fail observably rather than assigning the message to an arbitrary user.
- Preserve simulation semantics when adding real-webhook fallback. Share the core processor, but pass an explicit transport/fallback policy or wrap it at the webhook boundary.

TDD matrix:

1. Active sender identity saves under its own user even when the dedicated inbox has a different owner.
2. Unknown sender saves under the owner of the integration matching `recipient.id`.
3. Unknown recipient does not fall back to another integration/user.
4. Duplicate `message.mid` remains idempotent.
5. No sender username appears in configuration, migrations, or routing conditions.
6. Existing simulated-DM tests remain unchanged and green.

For live verification, send a signed event from an arbitrary unregistered sender ID, assert `notes.user_id == instagram_integrations.owner_user_id`, and clean the synthetic row. Then require one fresh real DM after deployment; pre-deployment messages may not be redelivered.

## Observability design

A production webhook may safely log structured metadata such as delivery timestamp, event count, outcome category (`ignored`, `unmatched`, `deduplicated`, `processed`, `failed`), and hashed/truncated identifiers. Never log access tokens, app secrets, verification tokens, signatures, raw payloads, or message text. Without outcome telemetry, `200` responses can hide application-level drops.

## Related cautions

- `conversations: []` does not prove all permissions, roles, app-mode rules, or thread visibility are correct.
- Provider error subcodes do not prove the entire authorization path succeeded unless their documented semantics and original request context are verified.
- The 24-hour messaging window generally constrains business-initiated replies; it does not explain failure to ingest a fresh user-initiated inbound message.
- Publishing/Live mode cannot fix a missing callback route or an internal recipient-ID mismatch.
