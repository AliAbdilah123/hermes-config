# Hermes session-backed conversation branches

Use when an application models child conversations on top of Hermes Agent sessions.

## Core contract

- A branch must be a real Hermes session fork, not a new arbitrary session ID plus reconstructed transcript.
- Create it with `POST /api/sessions/{source_session_id}/fork` and JSON `{ "id": "<requested-child-id>", "title": "<title>" }`.
- Validate the response object and persist `session.id`; verify `session.parent_session_id` equals the requested source.
- Send the opening turn and later turns to `POST /api/sessions/{child_session_id}/chat` with `{ "message": "..." }`.
- Main conversations resolve their source from the latest real job session (for Paragentix, `job_runs.tmux_session = hermes-api:<id>`). Nested branches use their direct parent conversation's persisted Hermes session ID.
- Hermes currently forks the persisted parent transcript. A UI-selected message can remain local fork metadata, but do not claim point-in-time transcript truncation unless the API supports it.

## Multi-fork integrity

1. Validate all local inputs first.
2. Create every remote sibling fork before committing local branch rows.
3. If a later remote fork fails, delete already-created remote siblings where feasible.
4. If local persistence fails, clean up all newly created remote forks.
5. Start each child chat only after local persistence commits.

This is compensation, not a distributed transaction; make failures explicit.

## Completion persistence under concurrency

Several sibling chats may finish simultaneously. Do not silently drop SQLite completion writes.

- Call Hermes chat exactly once; retry only the atomic local completion transaction.
- Atomically append the reply/error event and move `active` to `ready_to_merge`/`waiting`.
- Retry boundedly only for SQLite `BUSY`/`LOCKED`, honoring shutdown cancellation and the configured busy timeout.
- Guard by conversation ID, job ID, active status, and session ID so an old completion cannot overwrite newer activity.
- After retries, attempt to persist an explicit error/`waiting` outcome and log if even that fails.

## Merge-back review contract

When a child conversation merges into its direct parent, prefer one editable summary field over a UI-managed list of extracted points.

- Prefill the field from only the unmerged delta: query events after the latest persisted source-event watermark.
- Keep the preview watermark and reject confirmation if newer events arrive before the merge transaction commits.
- Submit and return a single `summary` string; render it as one whitespace-preserving text block.
- Preserve direct-parent enforcement, authorization, active-reply exclusion, and idempotency-key semantics when simplifying the payload.
- If an existing JSON column stored arrays of points, avoid a schema migration when a compatibility reader can decode both the new JSON string and legacy array, joining old points into readable paragraphs.
- Validate non-empty and byte-length limits at the API boundary; ensure UTF-8-safe truncation when constructing the preview.

Focused regression coverage should prove: exactly one prefilled textarea; edited summary submission; no point controls/list rendering; rejection of the legacy request contract if intentionally removed; stale preview and racing-event rejection; duplicate idempotent response; delta-only preview after a prior merge; and compatibility reads of legacy stored arrays.

## Required tests

- Exact fork URL, auth header, and `{id,title}` payload.
- Returned child session ID and direct parent lineage are persisted.
- Main uses the latest job Hermes session; nested fork uses direct parent session.
- Opening and follow-up turns use the same child `/chat` endpoint.
- Partial multi-fork failure leaves no local children and compensates remote children.
- Concurrent sibling completions all persist, while each Hermes chat is called once.
- Run the concurrency regression repeatedly (`-count=10`) before delivery.
