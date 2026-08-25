# Nested subtask drag-and-drop verification

Use when adding persistent reordering to collapsible child rows that appear on several task-list surfaces.

## Implementation boundaries

- Keep same-status children in the existing nested/collapsible renderer. Do not flatten them into top-level status lists merely to make them draggable.
- Put the parent drag handle/ref on the visible parent row, not the wrapper containing its expanded descendants. A draggable parent subtree must not contain nested draggables.
- Give each expanded parent its own droppable namespace such as `subtasks:<parent-id>` and each child a stable draggable ID such as `subtask:<child-id>`.
- Reuse one shared reorder operation/cache update across homepage, all-tasks, goal cards, and other interactive surfaces. Avoid duplicating persistence logic in each page.
- Accept only same-parent drops unless reparenting is explicitly requested.
- When only a filtered subset is visible, preserve hidden siblings and their relative order. Never send a partial list that accidentally renumbers, drops, or interleaves hidden children incorrectly.
- Do not recursively enable child droppables unless nested subtask reordering is explicitly supported and the drag library permits the resulting nesting.
- Optimistically update order only with a captured previous state; on failure, roll back without overwriting a newer successful reorder.

## Review gates

1. Inspect every `DragDropContext`, `Droppable`, and `Draggable` boundary. Ensure a new context does not shadow an outer context needed for parent-task drag.
2. Confirm the cache is populated before deriving IDs. Initial embedded `task.subtasks`, fetched cache, filtered lists, and post-reload API order must agree.
3. Verify mouse/pointer and the drag library's keyboard flow. Interactive controls inside a row (expand, checkbox, edit, delete) must remain usable and must not unintentionally initiate drag.
4. Add a persistence regression at the API/store boundary: reorder two children, refetch by parent, assert order and unchanged `parentId`.
5. Add focused UI coverage or source assertions for both homepage and all-tasks wiring, nested/collapsed rendering, stable IDs, same-parent guard, and shared reorder call.
6. Run the focused regression and final frontend typecheck/build after the last edit.
7. Before browser mutations, preflight fixture eligibility on every requested route. A parent visible on All Tasks may need a Daily goal/date/status association to render on the homepage; create the minimum route-eligible parent and assert visibility on each surface before dragging.
8. Register fixture cleanup before creation and execute it in `finally`/an outer trap. Clean children, parent, route-enabling goal/container, and test identity where safe, then require zero rows for the unique IDs/prefix even when an assertion or locator fails.
9. For completion, exercise the authenticated public UI on each required surface: expand parent, reorder, reload, verify persisted order and clean console/network behavior.
10. Instrument drag simulation with drag-library announcements, DOM order, and persistence-request traffic. If a synthetic keyboard sequence emits no lift/drop and no request, treat it as a harness failure; validate pointer drag before changing product code, then test keyboard accessibility separately.

## Common false confidence

- A production build proves only compilation, not drag behavior.
- A passing reorder endpoint test does not prove the UI sends the complete correct sibling order.
- An autonomous agent's clean exit is a handoff; inspect the diff for nested-context and filtered-subset defects before commit.
- Enabling drag on every `TaskListItem` call site can create nested contexts or recursive draggables. Trace each rendered surface rather than relying on a global boolean prop.
- A missing homepage locator after successful All Tasks coverage may mean the fixture is ineligible for homepage rendering, not that the feature regressed.
- A failed synthetic key sequence is not product evidence unless the drag actually lifted; require announcements/DOM movement/request evidence.
- Cleanup placed after assertions is skipped on the first failure and strands production fixtures. Install cleanup first.
