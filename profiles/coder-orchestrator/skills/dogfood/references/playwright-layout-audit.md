# Playwright layout audit pattern

Use this when browser navigation is slow/auth-gated or the user explicitly asks for Playwright-based layout diagnosis.

## Pattern

1. Prefer read-only analysis unless the user explicitly asks to fix/deploy.
2. Start the app locally if needed, then use Playwright against the local route.
3. Seed auth state with localStorage/session cookies only in the Playwright context; do not alter production data.
4. Mock API responses with `page.route()` when the goal is visual/layout inspection and real data/auth would slow the audit.
5. Capture at least one desktop and one mobile screenshot.
6. Extract layout metrics with `getBoundingClientRect()` and relevant scroll widths:
   - container/header/tabs/main rects
   - gaps between header, tabs, and content
   - `document.body.scrollWidth` vs viewport width
   - mobile tab `scrollWidth` vs `clientWidth`
7. Triangulate visual issues with source causes by naming the component/CSS files and the exact classes/inline style patterns responsible.

## Report shape

- State clearly that no implementation/deployment was done if the request was analysis-only.
- Include screenshots as `MEDIA:/absolute/path` when available.
- Separate observed layout problems from source causes and recommended fix direction.
- Avoid inventing production behavior from a mocked audit; label it as local/mocked if applicable.

## Useful Playwright snippets

```js
await page.route('**/api/**', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify(mockBody),
}));

await page.evaluate(() => {
  localStorage.setItem('app.auth.token', 'fake');
});

const metrics = await page.evaluate(() => {
  const rect = (selector) => {
    const el = document.querySelector(selector);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height, top: r.top, bottom: r.bottom };
  };
  return {
    bodyWidth: document.body.scrollWidth,
    viewportWidth: innerWidth,
    header: rect('header'),
    main: rect('main'),
  };
});

await page.screenshot({ path: '/tmp/layout-audit.png', fullPage: true });
```
