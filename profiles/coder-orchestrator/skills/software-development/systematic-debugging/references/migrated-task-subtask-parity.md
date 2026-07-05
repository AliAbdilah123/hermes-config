# Migrated Task/Subtask UI Parity

When a migrated task app reports that subtasks no longer behave like the original UI across dashboard/list pages:

## Root-cause pattern

A migration can preserve CRUD endpoints for subtasks but lose the list-contract needed by the UI:

- main task/goal list endpoints return child tasks as flat top-level rows (`parent_id` not filtered)
- returned parent tasks omit `subtaskCount`, so expand/collapse controls never render
- a new page implements its own flat task row instead of reusing the recursive task-list item component
- subtask fetch endpoints return children, but those children omit their own counts, preventing nested expansion

## Triage

1. Create a parent task and at least one child task through the real API.
2. Probe the main task list and goal/dashboard task list endpoints.
3. Verify:
   - only top-level tasks appear in main lists (`parent_id is null` equivalent)
   - parent DTOs include `subtaskCount > 0`
   - child/subtask endpoint includes child DTOs and their own `subtaskCount`
4. Inspect affected UI pages for duplicated flat row rendering. Prefer one shared recursive task item.

## Minimal fix

Backend:
- filter primary list/dashboard goal task queries to top-level tasks
- add a helper that batches subtask counts for returned task IDs
- apply that helper to task lists, goal task lists, and subtask fetch results

Frontend:
- reuse the shared recursive `TaskListItem`/equivalent on every task-list surface
- keep page-specific actions like delete outside the shared row if needed

## Regression check

Add a test that signs up/authenticates, creates a parent task, creates a child with `parentId`, then requests the main task list and asserts:

- exactly the parent appears
- the child is not a top-level row
- the parent has `subtaskCount == 1`

This catches both flattened-list and missing-count regressions.
