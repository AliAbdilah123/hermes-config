# Instagram user sender to dedicated inbox

Use when an application-generated verification code must be delivered **from an ordinary configured Instagram account** to a separate dedicated inbox account.

## Credential roles

Keep these identities distinct:

- Dedicated inbox ID/token: receives inbound verification and note DMs; may send replies to the inbound sender.
- User sender ID/token pairs: originate application-triggered verification-code DMs to the dedicated inbox.
- Never use the dedicated inbox token as a sender fallback or allow its ID to be selected from the sender pool.

For Instagram Login messaging, send through:

```http
POST https://graph.instagram.com/{version}/{sender-account-id}/messages
Authorization: Bearer {sender-access-token}
Content-Type: application/json

{"recipient":{"id":"<dedicated-inbox-IGSID>"},"message":{"text":"<verification-code>"}}
```

Confirm that the recipient identifier is valid in the sender account's Instagram-scoped messaging context; a public/profile ID is not automatically interchangeable with an IGSID.

## Optional credential rollout

Supporting new optional environment keys must not force operators to populate them before deploying:

1. Teach the strict env parser all new keys so future config does not fail as unknown.
2. Load incomplete or absent sender pairs without startup failure.
3. Select only a complete `(account ID, access token)` pair.
4. Skip any pair whose account ID equals the dedicated inbox ID.
5. If no distinct complete pair exists, preserve the established manual verification flow; do not claim an automatic send occurred.
6. Do not fall back to the legacy dedicated-inbox credential pair.

Deterministic selection is sufficient for small fixed pools: first complete, distinct pair wins. Add health-aware rotation only when failures or volume require it.

## Failure ordering

Avoid persisting state that implies delivery when the provider call fails.

- New registration: if persistence must happen before sending, delete/rollback the pending identity on confirmed send failure. Prefer a transaction/outbox when stronger delivery guarantees are required.
- Code regeneration: attempt the send before replacing the stored hash, so a rejected send does not invalidate the user's existing usable code.
- Return only a sanitized application error; never expose provider response bodies or tokens.
- An HTTP 2xx proves Meta accepted the request, not that a human saw the DM. Live acceptance requires provider success plus confirmation in the receiving account when available.

## Regression matrix

- First complete distinct sender uses its own endpoint and bearer token.
- A sender pair matching the dedicated inbox ID is skipped.
- The next valid pair is selected deterministically.
- Recipient is the dedicated inbox messaging ID and text is the exact generated code.
- Missing/incomplete sender variables preserve manual verification and make no outbound request.
- Provider failure leaks no provider details and leaves no misleading new identity.
- Failed regeneration preserves the prior stored verification code.
- Existing inbound webhook verification and dedicated-inbox success replies remain unchanged.

## Verification boundary

Mocked request-shape tests prove local routing only. Before reporting success, inspect effective runtime key presence without printing secrets, restart the exact service binary after configuration changes, trigger the real flow, require Meta acceptance, and verify the DM reached the dedicated inbox. If credentials are absent, report live delivery as blocked rather than inferred from unit tests.