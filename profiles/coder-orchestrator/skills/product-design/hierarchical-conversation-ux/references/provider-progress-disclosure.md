# Provider progress disclosure

Use when a task conversation must retain intermediary provider updates without overwhelming the main transcript.

## Data boundaries

Separate:

- final assistant replies;
- non-empty assistant commentary/progress;
- structured assistant tool-call rows with empty content;
- tool arguments/results;
- authoritative job/run state.

Persist safe, non-empty commentary only. Do not expose raw tool payloads. A phrase such as “delegating to Codex” may be commentary, but delegation can also exist only as an empty-content tool-call row; never synthesize claims the provider did not expose as display text.

## Progressive disclosure

- Keep the final answer as a normal visible agent bubble.
- Group consecutive intermediary updates per run/turn in native `<details>`, closed by default.
- Summary: update count plus a short latest-status preview.
- Expanded body: chronological updates with timestamps.
- Keep errors and final replies outside the collapsed group.

## Processing state

Show `Provider is processing…` from authoritative running state, not from the presence or recency of progress messages. Add visible text plus `role="status"` and `aria-live="polite"`. Animation is supplemental and must stop under `prefers-reduced-motion`.

## Persistence pattern

Reuse the existing event table. Add an idempotency key unique per run: provider message ID when available, otherwise a deterministic standard-library hash. Poll the source session-message endpoint on the existing reconciliation cadence while a non-streaming completion request is active, and reuse the same synchronization helper during restart recovery. Reserve the completed assistant answer for the final-reply event so it is not duplicated as progress.

## Verification

- Delayed fake-provider test proves progress is stored before completion and repeated polling does not duplicate it.
- Reconciliation twice preserves count and order.
- UI test proves `<details>` starts closed and processing appears only while running.
- Public E2E checks the active animation/progress arrival and the completed state after refresh.
