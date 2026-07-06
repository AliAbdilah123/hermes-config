# SelfFlow list-layout subtask status drag

Use when SelfFlow homepage list layout must let subtasks move independently between status sections.

**Historical pitfall:** A flat-list + unconditional `hideSubtasks` approach was reverted repeatedly. The accepted corrected plan keeps same-status subtasks inside the parent’s collapsible rendering path and makes those nested rows draggable only after expansion. If a new request says “subtasks visible as top-level rows,” confirm that is intentional before reintroducing the flat-list behavior.

## Pattern

1. Keep `listEntries` selective. Preserve the parent-subtask exclusion for nested/same-status subtasks:
   - Exclude subtask entries when `parent && (!task.status || task.status === parent.status || !task.goalIds?.includes(todaysDailyGoal.id))`.
   - This prevents collapsed same-status subtasks from appearing as duplicate top-level rows.
2. Preserve `hideSubtasks={!!parent}` when rendering list entries:
   - Root task rows can expand/collapse subtasks.
   - Flat moved-subtask rows show parent context but do not recursively expose children.
3. In `TaskListItem.tsx`, split the draggable parent row from the collapsible subtree:
   - Add optional row props (`rowRef`, row draggable/handle props) and apply them only to the visible row `<div>`.
   - Add `renderSubtaskWrapper(subtask, index, node)` and use it only around nested subtask nodes.
   - Do not wrap the whole expanded `TaskListItem` subtree in one parent `Draggable`, or nested subtask drags can move the parent.
4. In `HomePage.tsx`, prefix drag IDs:
   - Root/list rows: `task:<id>`.
   - Expanded nested subtasks: `subtask:<id>` from `renderSubtaskWrapper`.
5. In `handleListDragEnd`, parse `task:` vs `subtask:`:
   - For `subtask:<id>`, find the task in `flattenedTasks`, not by `source.index` in the top-level source section.
   - On cross-section drop, update only that task/subtask status via `updateSubtask` and `api.tasks.update(id, { status, goalIds })`; keep `goalIds` including the current daily goal so it remains visible in the daily context.
   - Skip same-section reorder for nested subtask drags unless explicit nested ordering is requested.
6. Completed and other status sections remain normal droppable targets through the existing list droppable IDs (`list-inprogress`, `list-delegated`, `list-commitment`, `list-others`, `list-completed`).

## Verification

- Run `pnpm --dir packages/fe build` (or from repo root with the absolute package path).
- Deploy rebuilt `dist/` to the nginx-served SelfFlow frontend path.
- Verify the deployed HomePage bundle contains stable markers such as `Parent:` and `list-completed`.
  - `index.html` may only reference the entry bundle; `HomePage-*.js` is a lazy chunk named inside `assets/index-*.js`. If `grep` against the public index finds no `HomePage` asset, curl the entry JS and extract the lazy chunk name from there, then verify the marker in that public chunk.
  - On this deployment, the public domain can serve the SPA at `/` while nginx also exposes files under `/projects/self-flow/`; verify the asset URL that the served index actually points to, not just the filesystem path copied by `rsync`.

## Pitfalls

- Do not update only `status` for a subtask moved into the daily list. Without `goalIds` including the current daily goal, the subtask can have the right status but not be associated with the current Daily goal.
- Do not leave completed items outside DnD if the requirement says “other status” generally; collapsed sections can still be droppable if their content is wrapped correctly.
- If the user says expanded subtasks “below the parent task” cannot be dragged individually, the root cause is usually that the parent `Draggable` wraps the expanded `TaskListItem` subtree. Minimal fix: keep the `listEntries` parent guard, apply the parent draggable props only to the visible row, wrap nested subtask nodes with their own `Draggable`, and have `handleListDragEnd` resolve `subtask:<id>` from `flattenedTasks` before persisting `status + goalIds`.
- Avoid duplicating four near-identical Draggable render blocks. A tiny `renderListDraggableTask(entry, index)` helper is the smaller diff and preserves parent-title logic consistently.
