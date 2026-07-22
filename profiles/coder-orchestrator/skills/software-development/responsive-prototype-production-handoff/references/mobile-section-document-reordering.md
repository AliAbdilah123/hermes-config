# Mobile section document reordering

Use when a section belongs in one composition on desktop but must move to a different document position on mobile.

## Minimal pattern

1. Keep the desktop instance in its existing composition and wrap it with a narrow, page-specific class.
2. Render a mobile instance at the required semantic position in the DOM.
3. Hide the mobile instance by default.
4. At the mobile breakpoint, hide only the desktop wrapper and show the mobile instance.
5. Feed both instances the same filtered data, callbacks, routes, loading/empty states, and authorization/preview state.
6. Render the replacement only for entity types where it is relevant.

Prefer explicit DOM placement over CSS `order`: sticky tabs, landmarks, keyboard reading order, and scroll targets should match the visual sequence.

For a section requested “below the tabs,” verify the literal order is:

`tab bar < mobile section < relevant tab panel`

## Verification

Add one focused DOM-order assertion using `compareDocumentPosition`. Since CSS-hidden content can behave inconsistently in accessibility queries under jsdom, select the uniquely classed mobile wrapper for this structural assertion.

Also verify the intended media query hides the desktop wrapper and shows the mobile instance. If canonical verification detection is unavailable, a temporary `/tmp/hermes-verify-*` source/DOM probe is acceptable, but report it as ad-hoc verification and remove it afterward.

## Pitfalls

- Do not hide a broad shared hero/right-column container if other entity variants still need its content; wrap and hide only the section being relocated.
- Do not duplicate IDs. Parameterize or refactor shared components that emit IDs before rendering two responsive instances.
- Do not place the moved section after the tab panel when the requirement says below the tabs.
- Source/CSS assertions prove structure, not visual quality; use exact-viewport screenshot/geometry QA for final visual acceptance when available.
