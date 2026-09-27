# Passive real Instagram webhook ID capture

Use when debugging requires the exact identifiers from a **real Meta-delivered DM webhook**, while outbound messaging, synthetic callbacks, and routing changes are forbidden.

## Minimal design

- Add capture at the authenticated, signature-validated webhook boundary, immediately after parsing each event and before ignore/routing predicates.
- Copy only the latest raw `sender.id`, raw `recipient.id`, raw `message.mid`, and a server-generated UTC `received_at` timestamp.
- Keep this temporary record in process memory only. Do not log or persist raw IDs, message text, signatures, tokens, or the full body.
- Expose it through an existing-session authenticated read-only endpoint together with:
  - the configured recipient ID from effective runtime configuration;
  - `recipient_matches_configured`, computed directly from raw `recipient.id` equality.
- Preserve the provider field name `message_mid`; do not rename it to a generic `message_id` in the diagnostic contract.
- The diagnostic endpoint must make no provider request, database write, or outbound message call.
- Do not modify event filtering, recipient matching, fallback ownership, note creation, verification, or reply behavior.

Example response shape:

```json
{
  "captured": true,
  "webhook": {
    "sender_id": "<raw sender.id>",
    "recipient_id": "<raw recipient.id>",
    "message_mid": "<raw message.mid>",
    "received_at": "2026-09-26T15:48:01.123Z"
  },
  "configured": {"recipient_id": "<effective configured ID>"},
  "comparison": {"recipient_matches_configured": true}
}
```

## Verification boundaries

1. Unit-test authentication, empty state, exact response shape, match, and mismatch. Fixtures are acceptable for these code-level regressions.
2. Build and deploy the exact service binary, restart it, and verify local health plus public unauthenticated rejection (`401`) for the debug endpoint.
3. After restart, the in-memory capture is intentionally empty. Ask the operator to send one fresh text DM manually to the configured inbox.
4. Do **not** POST a signed fixture, use a webhook simulator, or send a DM through the Graph API when acceptance explicitly requires a real inbound event.
5. Read the authenticated endpoint only after Meta delivers the fresh DM. Report the six requested values verbatim and identify the event by `received_at`/`message_mid`.
6. If no real event has arrived, status is **STOPPED — awaiting real inbound DM**, not READY. Passing unit tests, healthy deployment, or a synthetic fixture is not live-delivery proof.

## Operational cautions

- A service restart clears the capture; deploy before requesting the real DM.
- Capturing before ignore predicates observes the provider envelope without changing routing, including events later ignored by domain logic.
- A process-global latest-event slot is suitable only for short-lived single-process diagnostics. For concurrent replicas or durable audit requirements, use a deliberately designed protected diagnostic store—but not unless requested.
- Remove the endpoint and capture hook when diagnosis is complete because raw stable IDs are sensitive operational data.