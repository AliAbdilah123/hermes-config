# Clickable row → context drawer verification

Use when a list/card row should open a chat, inspector, or other contextual drawer.

## Minimal implementation

- Keep the row’s existing content and data model; reuse the existing drawer-opening path rather than adding a second flow.
- Put the stable context payload on the row when the whole row is the trigger.
- If the trigger is not a native button/link, add `role="button"`, `tabindex="0"`, an explicit accessible name, and activate it on both `Enter` and `Space` (`preventDefault()` for Space).
- Remove a now-redundant nested action button. Do not create nested interactive controls inside the row trigger.
- Keep unrelated row types unchanged when only one class (for example tasks) should gain whole-row behavior.

## Verification

1. Run canonical backend/frontend checks plus JavaScript syntax and diff checks where applicable.
2. Build the exact binary/artifact used by the service **before** restart. A source edit plus service restart can leave an old embedded static bundle live.
3. Restart, then poll the loopback listener/readiness endpoint rather than probing once immediately; process readiness can lag an active restart.
4. Fetch live HTML and assert its cache-busted asset URL identifies the new release.
5. On the exact public route, open the correct parent section, select a real row, and prove:
   - the drawer is open;
   - the attached context contains the selected row title/ID;
   - focus lands on the intended first control;
   - keyboard activation (`Enter`, and `Space` where practical) works;
   - the browser console has no errors.
6. Capture a non-empty screenshot when claiming visual verification.

A click handler existing in source is not sufficient evidence: the old embedded artifact, stale edge cache, wrong row type, or a drawer with incorrect context can all still fail the request.