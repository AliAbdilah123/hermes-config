# Radix Mobile Overlay and Restored-Control Regressions

Use this when a responsive refactor causes dropdowns/dialogs to leave the mobile viewport or removes controls from board/list containers.

## Diagnose

1. Inspect the primitive wrapper first (`DialogContent`, `DropdownMenuContent`), then every custom class passed into it.
2. For portalled Radix dropdowns, look for legacy positioning declarations on the custom class (`position:absolute`, `top`, `right`). They conflict with Radix/Floating UI's computed inline positioning. Let the primitive own placement.
3. Constrain dropdown height with Radix's available-height variable and a dynamic viewport ceiling:
   ```css
   max-height: min(70dvh, var(--radix-dropdown-menu-content-available-height));
   overflow: auto;
   ```
4. For dialogs, inspect both dimensions and scrolling. `max-height` alone still clips content. Use a `dvh` ceiling plus `overflow-y:auto`; retain a small viewport inset when the dialog remains centered.
5. If a control is “missing,” inspect rendered JSX before changing CSS. Compare Git history or the pre-refactor implementation. A removed button/action is not a responsive hiding bug.
6. Restoring a CRUD button requires the full workflow: per-container identifier in form state, form fields, submit/API branch, refresh, and error handling. Do not restore only the visible button.

## Minimal regression checks

- Assert custom dropdown CSS does not override primitive positioning.
- Assert the mobile dialog rule includes both a dynamic viewport max-height and vertical overflow.
- Assert each mapped container renders its action control.
- Exercise the form submission path, then run tests and a production build.
- After deployment, verify the public HTML references the new hashed assets; a healthy service alone does not prove the new frontend is served.

## Pitfalls

- CSS source-regex tests are useful as small guards in legacy/minified stylesheets, but keep assertions narrow. Avoid regex that assumes an event handler contains no `>` characters.
- Restarting a binary that embeds frontend assets requires rebuilding the binary after the frontend build, then waiting for the listener before probing it.
