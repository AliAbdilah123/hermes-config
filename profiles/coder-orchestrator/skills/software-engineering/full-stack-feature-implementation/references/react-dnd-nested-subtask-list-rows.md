# React DnD nested subtasks as independent list rows

Use when a React/Vite task list must let subtasks move independently between status sections.

## Pattern

1. Do not rely on nested child rendering when the child must be draggable independently.
   - A nested subtask inside a parent card is still visually/interaction-wise part of the parent drag surface.
   - Flatten parent tasks + loaded subtasks into list entries with `parentChain` metadata.
   - Render each entry as its own top-level `<Draggable draggableId={task.id}>` in the status droppable.
2. Hide nested subtasks in the list-mode row component when using flattened rows.
   - Add a narrow prop such as `hideSubtasks` to the shared row component.
   - In list/status-bucket mode, pass it unconditionally on parent and child rows; otherwise same-status children can remain nested inside the parent's draggable wrapper and dragging the child will carry the parent plus sibling subtasks.
   - Keep nested rendering for non-list contexts that still need expandable subtasks.
3. Preload subtasks broadly enough for the flattened list.
   - If the current page payload may omit/stale `subtaskCount`, do not gate loading only on `subtaskCount > 0`.
   - Fetch subtasks for each visible parent once, caching empty results to avoid loops.
4. Preserve parent context in the flattened row UI.
   - If a subtask status differs from its immediate parent, show a compact label like `Parent: <parent title>` above the subtask row.
5. On cross-status drop, update both status and current goal association.
   - Send `status` plus merged `goalIds` including the current daily goal id.
   - Optimistically update parent-goal rows if present; otherwise update the subtask cache.
6. Make every status bucket that should accept drops a real `Droppable`, including collapsed/optional sections such as Completed.

## Pitfalls

- If subtasks disappear after hiding nested rendering, the flattened list probably has no loaded subtask data. Check whether the preload logic depended on a count field that the page payload does not reliably include.
- If dragging a subtask moves the parent, the visible subtask is still rendered inside the parent card rather than as its own top-level draggable row. Common cause: a filter excludes same-status subtasks from the flattened list and leaves them nested under the parent; include them in the flat entries and hide nested children in list mode.
- Avoid a broad row-component rewrite; a single `hideSubtasks` prop plus flattened list rendering is usually enough.
