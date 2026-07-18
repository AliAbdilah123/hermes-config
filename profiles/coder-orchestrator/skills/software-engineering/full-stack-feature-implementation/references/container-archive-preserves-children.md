# Container archive must preserve children

Use when an action sits on a container header (column, lane, board, folder) and the user asks to archive that container.

## Semantic rule

- The button label should name the action, usually **Archive**, when its placement already identifies the target.
- Do not implement container archive by iterating over and deleting/archiving its children. That changes the wrong entities and can destroy history.
- Archive the container itself with a persisted flag/timestamp (for example, `archived_at` or `archived = 1`).
- Hide archived containers from active-list queries while retaining their children and relationships.
- Keep child-level archive actions separate and explicitly scoped to child detail/UI.

## Minimal implementation

1. Add an archive marker to the container schema using the project's migration convention.
2. Change the container archive endpoint to update that marker, tenant/owner scoped.
3. Filter active container listing queries by the marker.
4. Point the header button at the container endpoint and label it **Archive**.
5. Remove any client helper that loops through children.

## Verification

- Create/use a container with at least one child.
- Archive the container.
- Assert the container disappears from the active list.
- Assert the child row and its history still exist.
- Verify the deployed UI contains **Archive** and no misleading **Archive jobs/items** label.

## Pitfall

A successful UI disappearance is not enough: deleting every child can also make a column disappear or become deletable. Verify persistence directly so archival is proven non-destructive.
