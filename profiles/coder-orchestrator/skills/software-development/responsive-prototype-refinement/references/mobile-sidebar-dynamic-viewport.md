# Mobile Sidebar Dynamic Viewport

Use when controls at the bottom of a full-height mobile/tablet navigation drawer disappear behind browser chrome, especially on unfolded/foldable devices.

## Diagnose

1. Confirm the control exists in the DOM; distinguish viewport clipping from conditional rendering.
2. Inspect the drawer and flex children. A common structure is a column sidebar with scrollable navigation and a fixed footer.
3. Check for `height: 100vh`. Mobile browser chrome can make the layout viewport taller than the visible viewport, placing the footer below the screen.

## Minimal fix

Keep the legacy fallback, then prefer the dynamic viewport:

```css
.sidebar {
  height: 100vh;
  height: 100dvh;
}

@media (max-width: 900px) {
  .sidebar { height: 100dvh; }
}
```

Do not add resize listeners or JavaScript viewport calculations when CSS dynamic viewport units solve the issue.

## Verify

- Build and run existing tests.
- Deploy and confirm the served CSS contains the new declaration.
- Check the reported intermediate/fold viewport, not only phone and desktop widths.
- Open the drawer and assert the bottom control bounding box fits inside the viewport:

```js
const box = await page.locator('.mobile-sidebar .sidebar-logout').boundingBox();
assert(box && box.y >= 0 && box.y + box.height <= viewportHeight);
```

A generic public E2E may be stale or test only a phone viewport. If it fails for an unrelated selector ambiguity, report that separately and still run a focused viewport regression check; HTTP 200 or a CSS-string check alone is not visual proof.
