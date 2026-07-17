# OpenAI-Compatible Agent API Provider

Use this pattern when adding a remote agent (such as Hermes API Server) as a selectable execution provider beside local CLI delegates.

## Minimal vertical slice

1. Add the provider to the persisted per-user settings and provider selector.
2. Require and validate an absolute `http`/`https` base URL plus an API key when that provider is selected; make model/name configurable when the API accepts it.
3. Return only `api_key_set: true|false` from settings reads. Never send the stored key back to the browser. On updates, treat a blank key as “keep the current key.”
4. Call the provider through its documented OpenAI-compatible endpoint: `POST <base>/v1/chat/completions`, `Authorization: Bearer <key>`, JSON body containing `model` and `messages`.
5. Put a response-size ceiling on reads, reject non-2xx responses, and reject malformed/empty `choices` responses.
6. Route the remote result and errors into the application's existing run/event lifecycle instead of inventing a second job model.

## TDD checks

Start with a settings/API test proving:

- selecting the provider without URL/key returns 400;
- valid settings persist;
- the secret never appears in the settings response;
- subsequent blank-key updates retain the saved key.

Add an `httptest.Server` integration test for the execution adapter that verifies the request path, bearer header, model/message payload, successful response extraction, and controlled handling of provider errors.

## Schema migration pitfall

Do not casually rewrite `sqlite_master` to remove old provider `CHECK` constraints. Prefer a normal SQLite table-rebuild migration: create the replacement table with the expanded provider set, copy rows, drop the old table, rename the replacement, and recreate indexes/triggers inside a transaction. This avoids schema-cache/version hazards and keeps migrations auditable.

## Deployment verification

For Go binaries embedding a freshly built Vite SPA:

1. Build the frontend first so the embed directory contains the new asset hashes.
2. Rebuild the Go binary after that.
3. Restart the one service/process that owns the listen port. If systemd restart reports `address already in use`, identify the actual listener before retrying; a separately launched copy may still own the port.
4. Verify the served index references the new hash, the referenced asset returns 200, and the public bundle contains the new provider label.
5. Commit only after deployment verification. Preserve unrelated pre-existing working-tree changes.
