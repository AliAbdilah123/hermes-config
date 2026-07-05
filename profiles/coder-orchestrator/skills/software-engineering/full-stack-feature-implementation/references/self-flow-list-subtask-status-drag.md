# SelfFlow list-layout subtask status drag

Use when SelfFlow homepage list layout must let subtasks move independently between status sections.

## Pattern

1. In `packages/fe/src/pages/HomePage.tsx`, do not derive list sections only from `filteredDailyTasks` (root tasks). Use the existing `flattenedTasks` entries so loaded subtasks participate in list sections too.
2. Keep drag IDs unique. `flattenedTasks` may include the same task from both inline `task.subtasks` and `SubtasksContext`; dedupe by `entry.task.id` before rendering `Draggable` items.
3. Represent list sections as `EffortGroupEntry[]`, not `TaskDTO[]`, so a moved subtask keeps its `parentChain` metadata.
4. On cross-section drop:
   - Map destination droppable ID to the canonical task status (`list-inprogress` → `in progress`, `list-delegated` → `delegated`, `list-commitment` → `commitment`, `list-others` → `todo`, `list-completed` → `completed`).
   - Optimistically update root tasks via `setGoals` when present; otherwise update cached subtasks with `updateSubtask`.
   - Persist with `api.tasks.update(task.id, { status, goalIds: [...existingGoalIds, todaysDailyGoal.id] })` so dragged subtasks become associated with the current daily goal.
5. Render a small `Parent: <title>` line for entries where `entry.parentChain` has a parent whose status differs from the subtask status.
6. If users should be able to drag into Completed, wrap the completed collapsible content in a `Droppable` (for example `droppableId="list-completed"`) and include the placeholder inside it.

## Verification

- Run `pnpm --dir packages/fe build` (or from repo root with the absolute package path).
- Deploy rebuilt `dist/` to the nginx-served SelfFlow frontend path.
- Verify the deployed HomePage bundle contains stable markers such as `Parent:` and `list-completed`.

## Pitfalls

- Do not update only `status` for a subtask moved into the daily list. Without `goalIds` including the current daily goal, the subtask can have the right status but not be associated with the current Daily goal.
- Do not leave completed items outside DnD if the requirement says “other status” generally; collapsed sections can still be droppable if their content is wrapped correctly.
- Avoid duplicating four near-identical Draggable render blocks. A tiny `renderListDraggableTask(entry, index)` helper is the smaller diff and preserves parent-title logic consistently.
