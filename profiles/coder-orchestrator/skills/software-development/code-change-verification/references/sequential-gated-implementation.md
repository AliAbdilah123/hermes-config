# Sequential gated implementation

Use when an approved plan requires items to be implemented in an exact order and explicitly forbids carrying failures forward.

## Per-item gate

For each item:

1. Mark only that item active; all later items remain pending.
2. Give the coding agent only the current item, the already-verified prior state, explicit out-of-scope later items, and a no-commit/no-push constraint.
3. Require strict RED → GREEN evidence for the current acceptance behavior.
4. Treat the coding agent's success as a handoff, not verification.
5. Inspect the cumulative diff and independently run:
   - focused regressions for the current item;
   - the owning backend/package suite;
   - frontend tests when UI or contracts are touched;
   - production build/typecheck;
   - `git diff --check`.
6. Prefer one directly executed `/tmp/hermes-verify-itemN-XXXXXX.sh` with an EXIT cleanup trap so the gate is auditable and temporary files are removed.
7. Advance the task list only after every current-item check passes. If any check fails, keep the same item active, fix it, and rerun all affected checks; never defer it to a later item.

## Cumulative-workspace discipline

- Preserve verified earlier-item changes while constraining each agent to the next item only.
- Keep unrelated pre-existing files untouched.
- At each boundary, review `git status`, `git diff --stat`, and `git diff --check` so scope growth is visible.
- Do not commit intermediate items unless the delivery contract requests checkpoints. A final commit may contain all gated items after final integrated verification.
- If a delegated coding agent stops mid-milestone because of quota, provider, or transport limits after modifying files, treat the workspace as an untrusted partial handoff—not as a clean delegation failure. Inspect status/diff first, run the smallest focused test to locate the incomplete boundary, then continue directly or discard only clearly task-owned broken edits. Independently rerun the whole milestone gate afterward.

## Final gate

After all implementation items pass individually, run the complete integrated suite and required authenticated public E2E across every specified role. Per-item checks do not replace final cross-feature verification. Do not deploy, commit, push, or claim READY before this final gate when the user's completion contract requires it.

## Status language

Use **WORKING** only while execution is active. If interrupted, report **STOPPED** with the exact current gate. Use **READY** only after required public authenticated E2E passes.

When the user requests lower token usage, keep progress messages to one short line containing only the active phase, concrete blocker, or passed gate. Skip routine polling narration and repeated command details; reserve concise evidence for the final report.