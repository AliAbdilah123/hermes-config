# Protocol renderer and web-component verification

Use for prototypes whose visible UI is generated from protocol messages and rendered through custom elements or shadow DOM (for example, agent-driven UI renderers).

## Build the real path

- Use the actual renderer and protocol processor, not hand-authored HTML that merely resembles their output.
- Keep a small protocol-flow test that asserts surface creation, required components/actions, and state transitions.
- If TypeScript consumes messages authored in JavaScript, preserve or assert protocol literal types at the ingestion boundary; do not disable strictness globally.
- Treat dependency audit findings accurately. If an upstream package has no compatible fix, constrain the trust boundary (for example, bundled messages only), document it, and do not claim the audit is clean.

## Runtime verification

A successful compile does not prove the renderer produced a surface. After starting the production build:

1. Render the page in a real headless browser with enough virtual-time budget for custom elements to upgrade.
2. Inspect rendered DOM for text that can only come from the protocol-driven surface, not just the surrounding app shell.
3. Exercise at least one action and assert the resulting state text when browser automation supports interaction.
4. Verify desktop and mobile widths and check console/runtime errors.

React development remount behavior can expose lifecycle assumptions in stateful protocol processors. If the shell renders but the generated surface disappears under `StrictMode`, verify subscription/processor cleanup and remount safety first. For a small prototype, removing `StrictMode` is acceptable only when the production renderer is independently verified; production applications should make the integration remount-safe.

## Shadow DOM theming

Ordinary descendant selectors such as `.surface h1` do not cross a shadow boundary. A page can be structurally correct while renderer-owned headings remain unreadable.

- Inspect the renderer's documented CSS custom properties.
- Set inherited theme variables on the surface container and, when needed, directly on custom-element hosts (for example text/card hosts).
- Prefer variables such as on-background, text, surface, on-surface, border, and on-primary colors over brittle shadow-DOM manipulation.
- Take a public screenshot after deployment and verify contrast visually. DOM text presence alone is not visual evidence.
- Rebuild and redeploy after every styling fix; hashed CSS assets must change and the public screenshot must come from the new asset set.
