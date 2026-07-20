# Moving provider settings from account scope to workspace scope

Use this pattern when an integration/provider configuration must follow a workspace rather than its owning user.

## Data and migration

- Add provider URL, secret, and model fields to the workspace record with safe defaults.
- Backfill every existing workspace from its owner's legacy account settings so upgrades remain usable.
- Keep the migration restart-safe: detect whether workspace columns already exist before adding/backfilling them.
- Do not drop legacy columns in the same change unless compatibility and rollback requirements explicitly allow it.

## API and authorization

- Replace the account endpoint with a nested workspace endpoint such as `/api/workspaces/:id/settings`.
- Resolve workspace membership through the existing workspace route and permit reads to members while restricting writes to owners/admins.
- Never return stored secrets; return an empty secret plus a `*_set` boolean so blank submissions can mean “keep existing.”
- Validate provider URLs and require either a newly supplied secret or an already stored one.

## Execution path

Moving the form is insufficient. Trace every provider consumer and replace user-based lookup with workspace-based lookup:

1. Identify the workspace from the durable execution entity (job → column/board/project → workspace), not from the current user.
2. Pass `workspaceID` into new runs and retries.
3. Resolve workspace provider settings during restart/session reconciliation too.
4. Add tests proving two workspaces owned by one user do not leak settings.

## UI

- Put the settings UI inside workspace detail and make it a restorable URL/tab state.
- Remove the old account/avatar entry point and account dialog.
- Disable fields for read-only members, and hide the save action unless the role can write.

## Verification

- Test migration/backfill, authorization, cross-workspace isolation, new runs, retries, and restart reconciliation.
- Run frontend tests, backend package tests, full backend tests, and the production frontend build.
- For embedded SPAs, rebuild into the exact embedded asset directory, rebuild the service executable at its real `ExecStart`, restart it, and verify the live HTML references the newly generated asset hash.
