# Persisted managed resources and multi-selection

Use when replacing fixture-backed resources (tables, seats, rooms, stations, etc.) with locally or remotely persisted managed records, especially when transactions may select several resources.

## Migration and compatibility

- Introduce a stable resource ID plus editable display name; transactions reference IDs, while historical display remains readable.
- Migrate legacy status maps into complete records by overlaying saved statuses on seeded records. Do not let a partial legacy map erase defaults for absent IDs.
- Keep readers compatible with the legacy singular field while new writes use the plural ID field (for example, `table` for history and `tableIds` for new orders).
- Test both a partial legacy payload and a current-format reload.

## Management lifecycle

- Validate trimmed, case-insensitive unique names and positive integer capacity at the form/update boundary.
- Support add, edit name/capacity/status, enable/disable, and archive.
- Prefer archive over deletion whenever historical or active transactions can reference the resource. Show active-reference counts in management UI.
- Preserve archived records for historical rendering; exclude them from new selection.

## Consumer selection

- New selection lists enabled, non-archived, available resources.
- Retain any currently selected resource in the rendered choices even if its status changes, so state is not silently discarded before submission.
- Model multi-selection as an array of stable IDs and persist the array on the transaction.
- Clear selected IDs only when the active transaction is actually cleared/completed; holding or resuming must preserve them when draft round-trip is in scope.
- If the workflow requires at least one resource, disable submission and expose an explicit validation state when the selected array is empty.

## Availability summaries

For grouped availability such as `2 seats: 2/5`, compute:

- denominator: all non-archived records in the capacity group;
- numerator: enabled records whose status is available.

Render the summary once per capacity group and test exact numerator/denominator values after migration.

## Focused regression matrix

1. Partial legacy status map migrates without dropping seeded resources.
2. Add trims input; duplicate names and invalid capacities fail.
3. Edit changes name, capacity, and status and survives reload.
4. Referenced active resource archives rather than disappearing.
5. Disabled, archived, and unavailable resources are absent from new selection.
6. Multiple available resources can be selected and remain checked across unrelated cart edits.
7. Completed transaction persists ordered resource IDs; legacy singular transactions still render.
8. Capacity availability summaries match persisted state.

## Harness pitfalls

- A `<fieldset><legend>` is queried as role `group` with its accessible name, not with `getByLabelText`.
- A resource name may appear in both a grid button and detail heading; scope to role or container rather than using singular `getByText`.
- Update old single-select tests when the contract intentionally becomes checkbox multi-select; preserving stale query shape is not compatibility.
