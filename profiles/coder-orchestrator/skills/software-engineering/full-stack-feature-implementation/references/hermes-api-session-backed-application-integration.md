# Hermes API session-backed application integration

Use when a web application delegates chat execution and continuity to a Hermes Agent running on the same server.

## Discover the correct surface

Hermes may expose both a dashboard/backend server (commonly `hermes serve` / `hermes dashboard`) and a gateway API Server adapter. Do not assume the dashboard WebSocket is the best application integration merely because it supports JSON-RPC.

1. Inspect the installed Hermes CLI/source or current official docs.
2. Check the gateway status and the API Server health endpoint.
3. Call the authenticated capabilities endpoint and use the advertised contract. Current API Server capabilities may expose:
   - `POST /api/sessions` — create an empty persisted session;
   - `POST /api/sessions/{session_id}/chat` or `/chat/stream` — continue that session;
   - `GET /api/sessions/{session_id}/messages` — provider-owned history;
   - OpenAI-compatible chat endpoints with `X-Hermes-Session-Id` continuity.
4. Prefer the session-resource API when the application explicitly models conversations. It gives the application a durable Hermes session ID without making the application own the transcript.

## Minimal durable application model

Store only:

- internal conversation ID;
- project/workspace authorization boundary;
- nullable Hermes session ID;
- optional stable context-item reference;
- timestamps and recoverable error state.

Hermes remains the transcript owner. Do not mirror messages into the application database unless the product explicitly needs independent retention/search/export.

## Request sequence

1. Authorize the internal project/conversation.
2. For a new conversation, call Hermes session creation.
3. Persist the returned Hermes session ID **before** reporting that the conversation exists.
4. Send each turn to that exact session endpoint.
5. Apply the Bearer secret server-side; never accept a provider session ID or secret from the browser as authority.
6. If Hermes reports a missing/expired session, surface a recoverable error. Do not silently create a new session because that breaks continuity while appearing successful.

## Configuration and secret handling

- Put the Hermes URL and API secret in the application's deployment environment (`.env` or systemd environment file); commit only blank names in `.env.example`.
- When the same host already has a configured Hermes API Server, copy the values mechanically without printing them to terminal output, logs, review artifacts, or chat.
- Keep behavioral settings outside secret stores where the host convention distinguishes config from credentials.
- Bind Hermes to loopback when only local services consume it; expose the application, not the agent API.

## Verification

Use a fake authenticated Hermes HTTP server for focused tests:

1. The first application turn creates one Hermes session and persists its ID.
2. The second turn addresses the same Hermes session.
3. A separate application conversation receives a different session.
4. Invalid credentials and missing sessions fail closed.
5. The application database contains the Hermes session reference but no transcript body.

Before live release, probe the real Hermes capabilities endpoint with the configured credential without printing it, then run a two-turn public application E2E and confirm the stored session ID remains unchanged.

## Pitfalls

- Integrating against the dashboard authentication/ticket flow when the gateway API Server already provides a stable authenticated application API.
- Treating OpenAI-compatible stateless chat as continuous without sending the documented session continuity header.
- Persisting the provider session only after returning success.
- Logging authorization headers during curl/debug probes.
- Claiming Hermes chat is integrated when only a mock or health endpoint was exercised.
