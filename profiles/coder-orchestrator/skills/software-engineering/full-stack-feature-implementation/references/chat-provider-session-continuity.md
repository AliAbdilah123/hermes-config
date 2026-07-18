# Chat-provider session continuity

Use when an app sends multiple turns for one internal job/conversation to a stateful provider such as Hermes.

## Minimal durable model

- Store a nullable `provider_session_id` on the existing job, conversation, or AI-run record that defines the continuity boundary.
- A genuinely new job/conversation starts with no provider session.
- Before every outbound turn, load the stored ID and include `session_id` only when non-empty.
- After a successful response, read the provider-returned `session_id` and persist it before reporting success. This survives app restarts and prevents unrelated jobs from sharing context.
- Keep tenant/workspace authorization on the internal record; never accept an arbitrary provider session ID from the browser as the source of truth.

## Request path

1. Authorize access to the internal run/conversation.
2. Validate a non-empty message.
3. Query provider URL/model and persisted session in server-side storage.
4. Build the provider request with message/model and optional `session_id`.
5. Apply server-side credentials; keep provider secrets write-only.
6. Reject non-2xx responses with a bounded response-body read.
7. Decode the response and persist a non-empty returned session ID.
8. Return the provider result only after persistence succeeds.

## Migration

Add the nullable column to fresh-install SQL and to the app's additive/idempotent migration path for existing SQLite databases. Trace the actual startup migration call chain before editing.

## Focused test

Use an `httptest.Server` and a temporary/in-memory DB:

1. Insert one run with a null session.
2. First request must omit `session_id`; fake provider returns one.
3. Second request for the same run must contain that exact ID.
4. Assert the DB retained the ID.
5. Add a separate-run assertion when the surrounding suite supports it, proving sessions are not shared.

## Pitfalls

- In-memory maps lose continuity after restart and break across multiple service instances.
- Scoping the session to an AI user/provider account can leak context between unrelated jobs; scope it to the conversation boundary.
- Persisting only after a later background step risks losing the returned ID if the process exits.
- Do not invent a session ID for the first request.
- Provider session expiry/rejection should be handled explicitly according to provider semantics; do not silently reuse another run's session or globally clear sessions.
- A helper that is only exercised by a unit test is not an implementation: wire it into the real authenticated request/execution route and verify that route/build.
