# Goal/task selection sync bugs

Use when an edit modal lets users check/uncheck related tasks/items, the checkbox UI changes, but saving only adds items and never removes unchecked ones.

## Pattern

A common payload shape is:

- `currentTaskIds`: IDs currently linked when the edit modal opened.
- `selectedTaskIds`: IDs still checked when the user saves.
- `existingTaskIds`: IDs to add on create or from a separate add flow.

If the backend only loops selected/existing IDs and does `insert or ignore`, unchecking cannot persist. The API is treating the request as append-only instead of replacing/syncing the relation set.

## Root fix

At the relation owner update endpoint, when both current and selected sets are present:

1. Build a selected-ID set.
2. For each ID in `current - selected`, delete the junction row scoped by owner and user.
3. If a legacy single-FK column mirrors the relation (for example `tasks.goal_id`), clear it only when it points to the owner being removed.
4. Then run the normal insert/upsert loop for selected IDs.

For SQLite/Go handlers, keep deletes user-scoped, e.g. delete from the junction table only when an `exists(select 1 from tasks where id=? and user_id=?)` guard passes.

## Regression test shape

- Create a goal.
- Create two tasks linked to that goal.
- PUT the goal with `currentTaskIds=[keep, remove]` and `selectedTaskIds=[keep]`.
- GET the goal and assert `taskCount == 1` and only the kept task remains.

This catches the append-only backend bug even when the frontend checkbox state is correct.
