# Mobile Viewport + Authenticated Visual Checks

Use when a responsive bug report includes mobile/small-screen overlap or when screenshots show desktop layout squeezed into a phone viewport.

## Durable lessons

- A Vite/React app can appear to have working CSS media queries but still render as a scaled desktop page on mobile if `index.html` lacks:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  ```
- Verify true mobile layout with runtime metrics, not just screenshot dimensions:
  ```js
  ({
    innerWidth,
    innerHeight,
    docClientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
    viewportMeta: document.querySelector('meta[name="viewport"]')?.content || null,
  })
  ```
  For a 390px visual check, `innerWidth` and `scrollWidth` should both be around `390`; `innerWidth: 980` usually means the viewport meta is missing.
- If the dashboard is behind auth, do not stop at the login screen. Authenticate in the browser context via the real login API, store the returned CSRF/session state the frontend expects, then capture the dashboard.
- For dashboard overlap bugs, inspect both visual layout and DOM metrics. Good checks include: no `scrollWidth > innerWidth`, no panel negative margins causing stacking, rows wrapping intentionally, and action buttons grouped so extra buttons do not occupy unexpected grid columns.

## Example authenticated visual-check flow

1. Build and deploy the updated `dist/` to the nginx-served path.
2. Launch headless Chromium with a clean profile and CDP enabled.
3. Navigate to the app origin.
4. Run an in-page login fetch with `credentials: 'include'` and save the returned CSRF token to the same storage key the app uses.
5. Navigate to the dashboard route and wait for data to render.
6. Capture desktop and true-mobile screenshots.
7. Evaluate `innerWidth`, `scrollWidth`, and viewport meta; report the real metrics.

## Pitfall

A screenshot file being 390px wide is not enough proof of responsive behavior. Without the viewport meta, mobile browsers can render a 980px layout scaled down into the screenshot, hiding the real overflow problem.