# Controlled modal mutation contracts

Use when a create/edit modal is controlled by a parent (`open` + `onOpenChange`) and exposes both ordinary submit and “create another” behavior.

## Trace both contracts

1. Trace the mutation payload through frontend DTO, API handler, persistence, and reload. Similar names are not interchangeable (`existingSubtaskIds` vs `selectedSubtaskIds`). For relationship edits, distinguish append-only input from desired replacement state.
2. Trace modal ownership through every parent caller. A child’s `closeAfterSave=false` is ineffective if `onSaved` unconditionally sets parent `open=false`.
3. Treat callback completion and final visibility as one ordered operation: await `onSaved` when it may refresh parent state, reset the form, then explicitly set the controlled state required by the action. Ordinary submit closes; “create another” remains open.
4. Check creation separately from update. Creation may use an append/link payload, while update may need `current IDs + selected IDs` so the server can detach `current - selected` and attach the final selection.

## Focused regression matrix

- Create with one checked existing child: request contains that child and persistence survives reload.
- Update with one retained, one removed, and one newly checked child: removed link is detached; retained/new links remain.
- “Create another”: first mutation succeeds, parent refresh callback runs, modal remains visible, and fields reset.
- Ordinary create/save: mutation succeeds and modal closes.

A mocked request-shape test is useful but does not replace a persistence assertion for relationship updates. For deployed work, exercise the exact authenticated public modal and confirm state after reload.

## Dirty shared-checkout boundary

If the relevant backend implementation lives inside a large unrelated untracked extraction, do not commit only the small tracked caller when that commit would not compile from the remote baseline. Either reproduce the task-owned delta in a clean worktree against an integrated baseline, or stop at the integration boundary and report the passing local evidence precisely. Never absorb the entire unrelated extraction merely to make the fix committable.