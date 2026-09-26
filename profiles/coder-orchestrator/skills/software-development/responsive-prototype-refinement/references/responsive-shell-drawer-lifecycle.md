# Responsive shell drawer lifecycle

Use this focused pattern when a desktop sidebar becomes a mobile overlay drawer.

## State lifecycle

- Close the drawer on pathname changes so navigation cannot leave a stale overlay open.
- Close it when a `matchMedia` listener crosses back into the desktop range.
- Feature-detect `window.matchMedia`; non-browser renderers such as jsdom may omit it. Missing support should skip resize synchronization, not crash rendering.
- Add the body scroll-lock class only while open and always remove it in effect cleanup.

## Overlay and focus

- Render a backdrop above page content and below the drawer.
- Escape and backdrop activation close the drawer and restore focus to the menu trigger.
- Move focus to the first drawer action after opening.
- Trap Tab and Shift+Tab within drawer actions while open.
- Preserve explicit accessible control relationships with `aria-expanded` and `aria-controls`.

## Narrow header priorities

At narrow widths, keep global actions reachable and shrink decorative content first:

1. hide the brand subtitle;
2. elide or remove the decorative logo at phone widths;
3. constrain the business selector;
4. retain menu, messages, and theme controls with at least 44px targets.

Do not hide business context or critical global actions merely to make the header fit.

## Verification gate

Run a focused shell regression immediately after the change. If it fails because a browser API is absent in the test environment, add a safe capability check in production code when the API is genuinely optional; do not require every renderer to polyfill it. Then rerun the exact same regression before advancing to feature-page responsiveness.
