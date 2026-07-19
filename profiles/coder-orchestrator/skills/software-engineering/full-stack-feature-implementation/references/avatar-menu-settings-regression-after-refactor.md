# Avatar-menu Settings regression after frontend refactor

Use when an authenticated avatar menu loses **Settings** even though settings previously existed.

## Diagnosis

1. Search current avatar/account-menu markup for the missing action.
2. Search Git history for the last working `Settings` callsite and form; recover the complete workflow rather than adding a dead label.
3. Confirm the authenticated settings API still exists and retains its privacy boundary (logged-out request returns `401`).
4. Check whether the refactor removed both:
   - the menu action that fetches settings and opens the dialog;
   - the settings state/form/save path.

## Minimal restoration

- Add **Settings** to the active avatar menu.
- On click: close the native `<details>`, fetch `/settings`, populate existing settings state, and open the settings dialog.
- Restore the existing provider/delegate fields and PATCH save behavior from Git history. Do not invent a replacement settings model.
- Preserve write-only secret behavior: API keys render blank with a “saved” indicator and blank submissions retain the stored key.

## Test-first check

Add a focused source/DOM regression asserting the active app shell contains the Settings action and characteristic form labels. Run it first and confirm it fails because the refactor removed them, then restore the workflow and run the full frontend and backend suites.

## Deployment trap

A successful build to a repository-root binary does not update a systemd service whose `ExecStart` points to `bin/<app>`. Inspect the unit, build to the exact `ExecStart` path, restart, then verify the public index references the new asset hash. Confirm the new public JS asset contains the Settings marker.

## Root-cause wording

Report this as a refactor regression: the active frontend shell dropped the Settings action/dialog while the authenticated backend settings endpoint remained available.
