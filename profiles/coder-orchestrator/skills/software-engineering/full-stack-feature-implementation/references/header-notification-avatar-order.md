# Header notification and avatar ordering

Use this for small topbar requests such as moving a notification bell immediately left of the user avatar.

## Minimal implementation

1. Inspect the active app shell, not legacy/duplicate header code.
2. Group the notification center and account/avatar menu in one wrapper, in the requested DOM order:
   ```tsx
   <div className="header-actions">
     <NotificationCenter ... />
     <AccountMenu ... />
   </div>
   ```
3. Give the wrapper only the layout needed: `display:flex`, `align-items:center`, and a small `gap`.
4. Keep notification/account dropdown positioning relative to their existing `<details>` elements; do not rewrite either component.
5. Check mobile rules that previously positioned `.account` absolutely. Move that positioning responsibility to the wrapper or remove the stale rule if it breaks adjacency.

## Verification

- Run the native frontend tests and production build.
- If Go embeds the frontend assets, rebuild the Go binary after the frontend build, then restart the service.
- A service can report `active` just before its socket is ready. Verify readiness from its startup log or retry the local HTTP request briefly instead of treating the first connection refusal as deployment failure.
- Confirm the public index references the new asset hashes and the deployed JS/CSS contains the new wrapper marker.
- For visual-only changes, supplement marker checks with a screenshot when practical.

## Source control

Deploy and verify before committing. Push only when a remote exists; report a missing remote plainly rather than implying delivery upstream.
