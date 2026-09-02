# Reparented Children Hidden by Status Filters

Use after repairing an accidental `parent_id` change when expanding the restored parent still displays nothing.

## Cross-layer diagnosis

1. Query the parent and all children directly, including each status, goal relation, and owner.
2. Probe the child-list API separately. Correct database rows do not prove the UI will render them.
3. Trace both top-level and nested render predicates. A disappearance trap is:
   - top-level rows exclude every item with `parentId`;
   - nested rows require child status to equal parent status/current section;
   - differently-stated children are therefore rendered nowhere.
4. Distinguish completed-child hiding from accidental total hiding. Preserve an explicit “Show N finished subtasks” control, but active children must appear when expanded even if their status differs from the parent.

## Safe data repair

- Resolve the destination parent uniquely by owner and exact ID/title.
- Back up SQLite with `.backup` or the SQLite backup API.
- In one transaction, update only enumerated child IDs scoped by owner and current accidental parent.
- Assert the exact affected-row count before commit.
- Verify `PRAGMA integrity_check`, zero remaining children under the accidental parent, and every expected child under the destination.

## Regression matrix

- Create/edit dialog: stale selected child IDs must be reset before a new create request.
- API: only IDs explicitly selected in the current interaction may be reparented.
- Homepage: an in-progress parent with todo children expands visibly.
- Finished behavior: completed/not-done children remain reachable through the finished-child toggle.
- Public delivery: verify the authenticated deployed homepage using the affected hierarchy; build and API checks alone are insufficient.
