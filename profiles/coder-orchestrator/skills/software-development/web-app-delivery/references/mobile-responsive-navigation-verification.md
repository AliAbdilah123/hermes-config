# Mobile Responsive Navigation Verification

Use this reference when changing app-shell/sidebar/topbar layouts for small screens.

## Pattern

For desktop-first dashboards with a persistent sidebar:
- Keep desktop sidebar behavior unchanged above the breakpoint.
- Add a mobile-only hamburger button in the topbar/header.
- Move the existing nav into a drawer/overlay rather than duplicating menu content.
- Include `aria-label`, `aria-expanded`, and `aria-controls` on the hamburger button.
- Give the drawer an accessible label and a close button.
- Add a backdrop and close on backdrop click.
- Close on nav item click and Escape where straightforward.
- Ensure page content is not horizontally squeezed: topbar actions, cards, grids, list rows, and CTA panels should wrap/stack cleanly.

## Verification

Minimum checks before reporting done:
1. Run the normal frontend build (`npm run build` for Vite projects).
2. Deploy/copy the new `dist/` output to the nginx-served project directory if the user expects the live URL to update.
3. Verify nginx serves the new asset names from `index.html`.
4. Capture a real small-viewport screenshot, e.g. `390x844`, with headless Chromium.
5. Confirm the screenshot shows the hamburger/topbar and no persistent sidebar at mobile width.
6. Provide the screenshot as evidence when useful.

## Pitfalls

- A successful build is not enough; the public nginx route can still be serving stale assets if `dist/` was not copied.
- Do not let mobile screenshots silently hit a login/empty state if the requested layout is behind an authenticated/demo route; seed or use the app's existing demo state as appropriate.
- Avoid mobile CSS that merely shrinks the desktop grid; stack dense rows/cards to prevent horizontal overflow.
