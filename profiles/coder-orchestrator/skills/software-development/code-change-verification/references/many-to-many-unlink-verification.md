# Many-to-many unlink verification

Use when a UI action removes selected records from a container such as a day goal, project, collection, or tag.

## Contract audit

Before choosing a generic field update, trace how membership is actually read:

- legacy/direct foreign key on the child row;
- junction table used by list/detail queries;
- compatibility fields synthesized from junction rows.

A request that sets the direct foreign key to `NULL` is not an unlink if rendered membership comes from the junction table. Prefer an existing container-update/unlink contract that synchronizes both representations. Add a dedicated endpoint only when no existing contract safely expresses the operation.

## Focused regression

Assert all of the following:

1. Only selected IDs are submitted for removal.
2. Unselected siblings remain linked.
3. The UI refreshes after success and clears selection.
4. The action is disabled while updating and when no current container exists.

Mocks must assert the exact request payload, but they are supporting evidence only because they can encode a false backend assumption.

## Public persisted E2E

Use a dedicated authenticated fixture through the public route:

1. Create the container and at least two linked records.
2. Select one record in the real UI and invoke unlink.
3. Verify the selection clears and the removed record disappears from the container after refresh/reload.
4. Query the real public API or runtime database and assert the junction row is absent; also assert the sibling junction row remains.
5. Remove the fixture account/tenant and require zero matching rows plus database integrity success.

If the UI appears successful but persisted membership remains, classify this as a contract defect—not an E2E harness failure—and stop completion/deployment claims until corrected.
