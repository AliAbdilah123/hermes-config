# Async private AI upload delivery

Use this pattern for authenticated multi-file uploads that must return before AI processing completes.

## Minimal durable shape

- Persist the parent record and ordered file metadata first.
- Store private files outside the public document root with restrictive permissions.
- Authenticate and authorize every metadata, mutation, and file-serving endpoint.
- Commit the database transaction before enqueueing background work.
- Return `202 Accepted` with the durable record ID and processing state.
- Persist lifecycle states such as `draft`, `processing`, `ready`, `failed`, and `finalized`, plus bounded error text and validated structured output.
- On process startup, move orphaned `processing` records to retryable `failed` unless a durable queue can prove ownership.
- When an in-memory queue is full, persist `failed` rather than silently losing the job.

## Provider boundary

- Keep provider URL, key, and model server-side and environment-driven.
- Send ordered images together when they represent one logical document.
- Bound HTTP timeout and response size.
- Validate the provider envelope and extracted JSON separately.
- Do not fabricate unreadable fields. Represent unknown optional values explicitly (for example `null`) and let the review UI correct them.
- Test the provider adapter with a local HTTP test server: authorization header, configured model, all images, malformed envelope, non-2xx response, and structured-output validation.

## Upload boundary

- Enforce body, file-count, and per-file size limits both client- and server-side.
- Validate supported image media types server-side; never trust filename extensions.
- Preserve explicit image order in durable metadata.
- If ordering is promised, provide actual accessible reorder controls or drag/drop—not just append/remove.
- Revoke browser object URLs after removal, cancellation, or successful upload.

## Verification ladder

1. Focused backend tests: ordered persistence, ownership, worker state transition, malformed AI output, restart recovery, retry/finalize rules.
2. Frontend typecheck and production build.
3. Deploy backend binary and SPA separately; poll local health after restart.
4. Public authenticated API E2E: create identity/session, upload multiple images, observe `processing`, poll to `ready`, retrieve an owned private image, finalize, confirm finalized listing, and confirm anonymous access is rejected.
5. Public authenticated browser E2E: open capture UI, attach multiple files, reorder, upload, observe ready/retry state, edit if needed, finalize, and verify the finalized tab. Capture console/page errors.

API E2E is strong backend evidence but does **not** replace browser E2E. If browser signup/navigation fails, inspect the app's actual auth contract and locators, repair the harness, and rerun. Do not mark browser E2E complete or say `READY` based only on API state transitions.

## Deployment pitfall

Confirm environment values are written to the exact `EnvironmentFile` consumed by systemd. Building from a nested backend directory can make a relative `.env` land beside the module while the service reads the repository-root `.env`. After restart, verify the effective environment-file path without printing secret values, then exercise a real provider-backed job.
