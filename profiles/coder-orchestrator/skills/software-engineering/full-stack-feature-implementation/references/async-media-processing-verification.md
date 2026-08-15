# Async provider-backed media processing verification

Use this checklist for authenticated upload flows that persist media and process it asynchronously through an AI/provider API.

1. Inspect the deployed service definition and identify its actual `EnvironmentFile`. Nested build working directories are not evidence that a nested `.env` will be loaded.
2. Deploy/restart, verify health, then upload the maximum meaningful shape (for example, two ordered receipt images) through the public authenticated endpoint.
3. Poll the durable record through a terminal state. A successful `202 Accepted` proves only upload/queueing, not provider processing.
4. Verify owned media retrieval succeeds and anonymous/cross-owner access is denied.
5. Use semantically meaningful images for extraction E2E. Blank or solid-color fixtures test transport and authorization only.
6. Model unreadable fields as unknown (`null` or empty when the schema permits), never fabricate values. Distinguish malformed provider output from legitimate uncertainty, and require missing required fields before finalization rather than before draft creation.
7. Verify restart recovery of `processing` jobs and retry transitions even if the runtime queue is in-memory.
8. Exercise the user-facing review/edit/finalize path. READY requires a real provider-backed job reaching the expected state and successful finalization.

Interpret failures by boundary: upload validation, durable persistence, queue transition, provider request/response, schema validation, authenticated media serving, or finalization. Fix and rerun from the earliest affected boundary.