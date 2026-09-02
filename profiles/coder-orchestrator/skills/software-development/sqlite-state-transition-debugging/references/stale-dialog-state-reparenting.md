# Stale Dialog State Reparenting

Use when creating a parent record unexpectedly moves older children from unrelated parents.

## Evidence path

1. Query the new parent and its children from the active SQLite database.
2. Compare timestamps: children older than the parent were reassigned, not newly created.
3. Inspect the create payload for relationship IDs such as `existingSubtaskIds`.
4. Trace reusable create/edit dialog state. Clearing visible fields is insufficient if relation-selection state survives a mode/task change.
5. Trace the server loop that consumes IDs. A create handler that runs `UPDATE child SET parent_id=? WHERE id=?` turns stale client IDs into destructive reparenting.

## Minimal correction

- Reset every relationship-selection state when entering create mode and whenever the edited record identity changes.
- Build create relationship IDs only from explicit selections made in the current create session.
- Keep edit preservation state separate from create selection state; never union previously loaded children into a new-parent payload.
- Prefer a distinct explicit move/reparent operation. At minimum, reject ordinary create requests that attempt to take a child already assigned to another parent.

## Regression checks

1. Edit parent A and load/select its children.
2. Close it, open a blank create dialog, and create parent B without selecting children.
3. Assert B has no children and A retains all children.
4. Assert the create request omits or empties `existingSubtaskIds`.
5. Add a server test proving ordinary create cannot silently take a child from A.

Report both boundaries: stale frontend state supplied the IDs, and backend create semantics converted them into persisted `parent_id` updates.
