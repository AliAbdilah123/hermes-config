# Responsive UI Regression QA

Use this when a user reports that a page is "not responsive like the original" or a responsive layout regressed after upstream/design migration.

## Investigation pattern

1. Identify the shared component used by the affected routes before editing route-specific pages.
   - Example: `/login` and `/signup` often share an auth/banner/aside component; fix the shared component first.
2. Compare against the original/reference implementation when available, but do not blindly restore fixed inline dimensions.
   - Fixed `style={{ width, height, padding, fontSize }}` values commonly caused the regression.
   - Convert fixed sizes and positions to breakpoint-aware utility classes.
3. Check the layout wrapper around the shared component.
   - A child can be responsive but still fail if the parent is hidden at the wrong breakpoint or has `h-full` without a concrete parent height.
4. Preserve desktop intent while adding tablet/mobile behavior.
   - Keep the full-height side panel at large widths.
   - At intermediate widths, allow the same banner to become a shorter top panel rather than hiding it entirely.
5. Verify at multiple viewport widths, not just the current desktop size.

## Visual verification tips

- For Vite apps with a non-root `base`, navigate to the full base path (for example `/projects/<app>/login`) when using a dev server.
- When taking Chromium headless screenshots of lazy React routes, use a virtual time budget so the screenshot is captured after Suspense/loading spinners settle:

```bash
chromium-browser --headless --no-sandbox --disable-gpu \
  --window-size=768,900 \
  --virtual-time-budget=8000 \
  --screenshot=/tmp/page-768.png \
  http://127.0.0.1:5173/projects/<app>/login
```

- Inspect both the breakpoint where the banner becomes a top panel (tablet) and the breakpoint where it becomes a side panel (desktop).
- Watch for horizontal overflow, clipped floating decorations, form accessibility, and whether the primary form is visible without being pushed off-screen unexpectedly.
