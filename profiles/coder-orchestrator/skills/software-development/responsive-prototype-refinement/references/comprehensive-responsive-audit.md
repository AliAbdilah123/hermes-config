# Comprehensive Responsive Audit Checklist

Use this reference for broad audits spanning several routes and interaction types.

## Discovery matrix

For every requested surface, record:

| User-facing name | Exact route/state | Primary component | Style owner | Wide-content owner | Overlay owner |
|---|---|---|---|---|---|

Do not assume every named experience has a standalone route. Verify nested tabs, drawers, and detail states.

## Root-cause order

1. Shell width, sidebar mode, and breakpoint state.
2. Document-level overflow and global clipping.
3. Flex/grid children missing `min-width: 0` or `min-height: 0`.
4. Feature-owned fixed/min widths.
5. Overlay stacking, focus, body lock, and safe areas.
6. Action visibility, wrapping, and touch targets.
7. Typography and spacing after structural defects are fixed.

## Viewport matrix

Include:

- spacious desktop;
- compact desktop/tablet landscape near the shell breakpoint;
- tablet portrait;
- the exact reported failing width and height;
- narrow mobile;
- desktop → mobile → desktop resize to expose stale state.

Width-only checks miss fixed-height workspace and soft-keyboard defects.

## Per-surface checks

### Shell and navigation

- Mobile navigation overlays content rather than consuming its width.
- Desktop collapsed state and mobile open state are independent.
- Route selection and breakpoint changes clear stale mobile state.
- Drawer has backdrop, Escape/outside dismissal, focus trap/restoration, body lock, and inert background.
- Account, notification, and critical global actions remain reachable.

### Tables and dense lists

- Overflow belongs to a local wrapper, never the document.
- Primary identity remains visible via sticky column/header or an equivalent mobile card.
- Rows and actions are keyboard-operable.
- Long identifiers, URLs, hashes, and notes wrap or truncate with disclosure.

### Forms, drawers, and modals

- Labels, validation, and task order survive stacking.
- Footer actions do not cover fields.
- Soft keyboard and safe-area insets do not hide the primary action.
- Nested overlays have unambiguous stacking and focus return.

### Maps and split panes

- Resizers are disabled or replaced for touch.
- Narrow screens use an explicit list/map mode rather than two tall stacked fixed-height panes by accident.
- Map overlays, errors, and result actions fit without collision.

### Timelines

- Dates remain readable; do not solve width by shrinking essential text below practical size.
- Metadata wraps without widening the page.

### Kanban

- Desktop/tablet horizontal scrolling stays local and discoverable.
- Narrow stacking happens only at an intentional breakpoint.
- Dragging has a visible keyboard/touch Move alternative.
- Bulk and card actions remain available.

## Browser assertions

At each route/viewport, assert:

```js
expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
```

Also verify:

- all critical actions are visible and enabled when business state permits;
- local wide surfaces have `scrollWidth >= clientWidth` when expected;
- controls intended for touch are at least 44×44 CSS pixels;
- focus stays inside open dialogs/drawers and returns to the trigger;
- Escape closes only the topmost overlay;
- resizing does not leave stale navigation or overlay state;
- no console errors or uncaught page errors occur.

Use authenticated deterministic fixtures when the routes require login. HTTP 200 and a successful build are supporting evidence, not responsive E2E.
