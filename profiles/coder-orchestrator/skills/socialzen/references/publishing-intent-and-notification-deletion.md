# Publishing intent, lifecycle labels, and notification deletion

Use this when saved workspace items cannot distinguish **Post now** from scheduled publishing, or when adding notification bulk deletion.

## Publishing intent is separate from execution state

Persist user intent explicitly (`DRAFT`, `NOW`, `SCHEDULED`). Do not infer **Post now** from `publish_at`, `created_at`, or timestamp proximity: both immediate and scheduled submissions may enter the same scheduler state, and the heuristic fails after reload.

Keep these invariants at every write boundary:

- Draft creation, duplication, or transition to draft => intent `DRAFT`.
- Immediate publication and every explicit retry => intent `NOW`.
- Future scheduled publication => intent `SCHEDULED`.
- Scheduler transitions (`SCHEDULED` -> `PUBLISHING` -> terminal) do not overwrite intent.
- Cancellation that leaves the parent in `DRAFT` resets intent to `DRAFT`; cancellation that leaves active publishing work preserves the prior intent.
- Reject contradictory combinations such as a non-draft post with `DRAFT` intent. Normalize draft writes to `DRAFT` defensively.
- Return intent from both list and detail DTOs; testing only the list boundary misses reload/edit defects.

For legacy rows, backfill drafts as `DRAFT` and all non-drafts conservatively as `SCHEDULED`; historical immediate intent cannot be reconstructed truthfully.

## UI presentation

- Scheduled intent: show its scheduled date/time and never a post-now countdown.
- NOW intent before due time: show an accessible countdown.
- NOW intent once due or while parent is `PUBLISHING`: show `Queued` and poll detail after reload until terminal.
- Destination presentation is product copy, not raw storage vocabulary: `DRAFT` -> `Post`; pending/uploading/publishing/review-required -> `Queued`; `PUBLISHED` -> `Posted`; retain failed/canceled states.

## Test-first matrix

Write focused failing tests before implementation for:

1. Migration backfill and idempotent preservation of explicit intent.
2. Create and edit payload persistence, contradictory combinations, list DTO, and detail DTO.
3. Retry forcing `NOW` through every retry endpoint.
4. Cancel-to-draft resetting `DRAFT` while active cancellation preserves intent.
5. Scheduled card versus NOW countdown, due transition, reloaded `PUBLISHING` polling, and terminal stop.
6. Destination copy mapping.

## Authorization-safe notification collection deletion

Use one authenticated collection endpoint accepting exactly one mode: explicit unique nonblank IDs (bounded, e.g. 1-100) or `all: true`. Decode JSON strictly, reject unknown fields and trailing documents, and retain the single-item endpoint for compatibility.

Inside one database transaction:

1. Build the selection with `user_id` in every count and delete predicate.
2. Count owned rows and owned unread rows.
3. Delete that exact owned set.
4. Return only owned counts so foreign/missing IDs are not distinguishable.

`all` should explicitly define whether archived rows are included; for a permanent delete-all control, include active and archived history and say so in confirmation copy. The UI must not remove rows optimistically, must preserve rows/selection on failure, and should adjust the unread bell using the server-returned unread deletion count.

Verify selected deletion, delete-all, malformed requests, unauthenticated access, mixed foreign/owned IDs, archived semantics, unread counts, and failure-state preservation.