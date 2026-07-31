# Hermes tool-progress timeline contract

Use when a job timeline supports collapsible intermediary/progress events but none appear.

## Diagnose the full boundary

1. Confirm the public bundle contains the collapsible renderer.
2. Count event kinds in the runtime database. Zero intermediary rows means the UI has nothing to group.
3. Compare the supervised process start time and executable with the latest backend build. A rebuilt binary is not deployed until the service is restarted.
4. Resolve the exact job run to its recorded `hermes-api:<session-id>` and fetch `/api/sessions/<session-id>/messages` from the workspace's configured Hermes URL.
5. Inspect the real message shape. Tool-driven sessions may encode progress as an assistant row with empty `content`, readable `reasoning`/`reasoning_content`, non-empty `tool_calls`, then a `tool` row containing raw result JSON.

## Safe normalization

For assistant tool-call turns, persist trimmed human-readable reasoning as intermediary progress only when `tool_calls` is present. Never expose raw tool arguments or tool-role result payloads; they may contain secrets, large diagnostics, or irrelevant internals.

Keep ordinary assistant content unchanged. Reserve the last normalized assistant message as the final reply and persist preceding messages as intermediary events with stable source keys. Accept numeric or string Hermes message IDs.

## Regression fixture

Use strict TDD with a fixture containing empty assistant content, emphasized readable reasoning, tool arguments with a sentinel secret, a tool result with another sentinel, and a final assistant response. Assert only cleaned reasoning becomes intermediary content, the final reply remains separate, and neither secret leaks.

## Delivery proof

1. Run focused normalization and persistence tests. If canonical command detection is unavailable, use a directly executed OS-safe `/tmp/hermes-verify-*` script and remove it afterward.
2. Run the broader backend suite and build from the module root.
3. Restart the supervised service after replacing the binary.
4. Exercise a fresh real job; old jobs cannot prove forward-only persistence.
5. Verify intermediary rows exist for that run and the exact public timeline renders them collapsed by default.
6. Treat tests, build, service health, persisted rows, and public browser behavior as separate evidence boundaries.
