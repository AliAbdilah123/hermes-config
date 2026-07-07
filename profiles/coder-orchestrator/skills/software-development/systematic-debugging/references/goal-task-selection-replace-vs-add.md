# Goal edit task selection: replace semantics vs add-only links

Use when a goal/project/category edit modal shows existing linked tasks/items with checkboxes and the user reports that unchecking an existing item does not remove it after save.

## Symptom

- The modal renders current linked tasks/items checked.
- Unchecking updates local UI state correctly.
- After saving/refetching, the unchecked task still appears under the goal.

## Root cause pattern

The frontend treats the checkbox list as the complete desired association set, but the backend treats the payload as an add-only list.

Typical frontend payload:

```json
{
  "selectedTaskIds": ["kept-task-id"],
  "currentTaskIds": ["kept-task-id", "removed-task-id"]
}
```

Broken backend shape:

```sql
insert or ignore into task_goals(task_id, goal_id) values (?, ?)
```

with no corresponding delete for `currentTaskIds - selectedTaskIds`. The unchecked ID disappears from React state but remains in the junction table.

## Investigation recipe

1. Read the modal state initialization: confirm current linked tasks seed the selected ID list.
2. Read the checkbox `onCheckedChange`: confirm uncheck removes the ID locally.
3. Read the save payload: look for both selected/desired IDs and current/original IDs.
4. Read the update handler: search for `insert or ignore` into the junction table and for any `delete from <junction>` using deselected IDs.
5. Check which source powers display/counts: if list/count queries join the junction table, stale links will keep rendering even if a legacy `tasks.goal_id` column changes.

## Minimal fix shape

On update, when both current and selected IDs are supplied:

1. Compute `removed = current - selected` server-side.
2. Delete only those links for the edited parent, scoped by user ownership.
3. If a denormalized direct FK exists (for example `tasks.goal_id`), clear it only when it points at this parent.
4. Insert selected IDs as before.
5. Add one regression test: create goal + linked task, update with `currentTaskIds=[task]` and `selectedTaskIds=[]`, assert the goal task count/list is empty.

Prefer fixing the shared update endpoint over hiding the task client-side; the stale junction row is the source of truth for future fetches.
