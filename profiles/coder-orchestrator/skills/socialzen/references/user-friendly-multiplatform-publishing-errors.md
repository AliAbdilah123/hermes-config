# User-friendly multi-platform publishing errors

Use this pattern when provider publishing failures leak raw diagnostics or cross-post status is ambiguous.

## Contract

Normalize failures once at the backend provider boundary. Each failed target should expose only:

- `errorCode`: stable application code
- `errorMessage`: safe plain-language copy
- `errorAction`: `RECONNECT`, `RETRY`, `EDIT_MEDIA`, `REMOVE_TARGET`, or `NONE`
- `recoverable`: boolean enforced by both API and UI

Initial useful codes: `CONNECTION_EXPIRED`, `INSUFFICIENT_PERMISSION`, `MEDIA_INVALID`, `NETWORK_ERROR`, `RATE_LIMITED`, `TARGET_UNAVAILABLE`, `CONTENT_REJECTED`, and `UNKNOWN_PUBLISH_ERROR`.

Unknown provider text must never be returned to clients. Log the raw error server-side with post ID, target ID, platform, and normalized code. Persist only safe fields in `post_targets`; the aggregate post message must be derived from safe target data rather than concatenated diagnostics.

## State and retry rules

- Present target states consistently as **Published**, **Failed**, or **Queued**; internal scheduled/publishing states may map to Queued.
- Derive parent state from targets: all published → Published; all failed → Failed; mixed published/failed → Partially published; queued with no failures → Queued.
- Retry only failed targets with `recoverable=true`.
- Never reset or republish already-published targets during partial retry.
- Hide Retry/Edit & Retry when no failed target is recoverable, and reject the same attempt server-side (safe 409/422 response).
- Every recoverable failure gets exactly one next action. Non-recoverable failures get no misleading retry CTA.

## Frontend reuse

Create one typed presentation helper/component and reuse it in Posts Card, Calendar Detail, Post Detail, and Edit & Retry. The component owns platform labels, display-status mapping, safe fallback copy, action labels/routes, partial-success wording, and `canRetry` derivation. Calendar API shaping must preserve target/error fields rather than reducing a post to only `Failed`.

## Minimal verification

1. Table-driven backend classifier tests, including unknown-error redaction.
2. API tests proving raw seeded provider markers never appear in JSON.
3. Mixed-target retry test proving successful targets are untouched.
4. Frontend tests for published+failed, queued+failed, unknown-safe fallback, and non-recoverable CTA absence.
5. Responsive checks on all four surfaces, then normal Go tests/build and frontend test/typecheck/build/deploy verification.

No external error framework or history table is needed for the first release; an ordered matcher, existing target rows, and backend logs are sufficient.
