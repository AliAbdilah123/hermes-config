# Native `<details>` menu: close on outside click

Use this for notification, account, or other dropdown menus implemented with native `<details>/<summary>` in React.

## Minimal implementation

Keep the behavior inside the reusable menu component rather than in a parent app shell:

1. Attach a `useRef<HTMLDetailsElement>` to the component's `<details>`.
2. In `useEffect`, register a document-level `pointerdown` listener.
3. If the event target is outside `ref.current`, set `ref.current.open = false` (or call the project's existing `closeDetails` helper).
4. Remove the listener in the effect cleanup.

`pointerdown` is preferable to `click`: it closes promptly and works across mouse, touch, and pen input. The containment guard preserves clicks inside the menu.

## Regression test

Render the real menu component in jsdom, locate its `<details>` through the accessible summary label, set `details.open = true`, dispatch `pointerdown` on `document.body`, and assert `details.open === false`.

Run the test before implementation and confirm it fails specifically because the menu remains open. Then implement and rerun the focused test plus the full frontend suite.

## Duplicate-app pitfall

Trace the active `createRoot(...).render(...)` path before editing. A repository may retain a legacy app shell with a similar notification menu. Put the fix in the component used by the active shell; do not patch only the legacy duplicate.

## Public bundle verification

After build/deploy, verify the new asset hash and behavior marker in the served bundle. Avoid `curl ... | grep -q ...` under strict pipelines because `grep` can exit early and make curl report write error 23. Download to a temporary file first, then grep the file.
