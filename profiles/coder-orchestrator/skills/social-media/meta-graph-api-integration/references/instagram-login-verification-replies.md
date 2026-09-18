# Instagram Login verification replies

Use this reference when an existing inbound Instagram DM flow must send a confirmation reply after activating a pending identity.

## Keep authentication topologies separate

For **Instagram Login with an Instagram User access token**, Meta's documented text-send contract (verified 2026-09-17) is:

- `POST https://graph.instagram.com/{GRAPH_VERSION}/{IG_ID}/messages`
- Header: `Authorization: Bearer <Instagram User access token>`
- Header: `Content-Type: application/json`
- Body: `{"recipient":{"id":"<IGSID>"},"message":{"text":"<TEXT>"}}`
- Permissions: `instagram_business_basic`, `instagram_business_manage_messages`
- The recipient must have initiated messaging with the professional account.

Authoritative overview:
https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api

Do **not** substitute the Page-linked Messenger contract (`graph.facebook.com/.../me/messages`, Page access token, `instagram_manage_messages`). Confirm the project's login topology and token type before implementation.

## Safe extension pattern

1. Preserve the existing verification transaction and identity lifecycle.
2. Atomically activate the identity and claim the inbound external event ID for one outbound attempt.
3. Commit activation before making the Meta network request.
4. Send only when the result proves: valid, unexpired, unused code; expected sender; successful activation; and ownership of the unique event claim.
5. Never send success for malformed, invalid, expired, unmatched, duplicate, already-consumed, or failed activation paths.
6. Keep the verification DM out of note/content ingestion.
7. Inject/mock the HTTP client in tests; assert host, bearer auth, recipient, payload, and exact attempt count without real credentials.
8. Never expose access tokens, raw provider errors, webhook payloads, or internal IDs to the UI.

## Idempotency limit

Meta's documented send request has no idempotency key. A database uniqueness claim can guarantee one **locally initiated send attempt** per inbound event, but cannot prove exactly-once external delivery across an ambiguous timeout or process crash. Do not automatically retry ambiguous outcomes; record a sanitized recoverable failure and require an explicit recovery policy if retries are later requested.

## UI status model

Keep permanent identity status minimal (`pending` and `active`) and represent verification feedback separately when practical:

- pending: code exists, user has not indicated sending
- waiting: frontend indication plus backend polling; never activate locally
- active: backend activation is authoritative
- invalid code: recoverable feedback, not permanent identity failure
- expired: derive from authoritative expiration; regeneration invalidates the old code
- system failure: sanitized recoverable feedback

Poll the existing identity-list/status API only while pending/waiting unless the product already has real-time infrastructure. Do not add WebSockets solely for this flow.

## Scope discipline

A verification-reply/status task does not justify account discovery, username search, autocomplete, dropdowns, Business Discovery, profile lookup, or arbitrary account lookup. Preserve manual username entry unless explicitly asked otherwise.
