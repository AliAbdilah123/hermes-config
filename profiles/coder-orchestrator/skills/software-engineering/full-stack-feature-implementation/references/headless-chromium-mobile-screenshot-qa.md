# Headless Chromium mobile screenshot QA

Use when you need to visually verify a deployed SPA on mobile viewport but the Hermes browser tool times out or hangs on the heavy JS bundle.

## When this applies

- Hermes `browser_navigate` / `browser_vision` times out (60s) on a large Vite/React SPA with big bundles or PostHog/framer-motion.
- You need a narrow-viewport screenshot to confirm responsive layout after deployment.
- No Playwright/puppeteer dependency is installed; system Chromium is available via snap.

## Working command

```bash
mkdir -p /home/ubuntu/<project>-qa

chromium-browser \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --window-size=390,844 \
  --virtual-time-budget=5000 \
  --run-all-compositor-stages-before-draw \
  --screenshot=/home/ubuntu/<project>-qa/page-mobile.png \
  'http://<host>/<path>#<anchor>' \
  > /home/ubuntu/<project>-qa/chromium.log 2>&1
```

Then use `vision_analyze` with the screenshot path to inspect layout, overflow, and responsiveness.

## Key flags

- `--virtual-time-budget=5000` — advances virtual clock so lazy/async rendering and animations settle before the screenshot is taken. Without this you get blank or partially rendered pages.
- `--window-size=390,844` — iPhone-class mobile viewport. Use `1440,900` for desktop QA.
- `--run-all-compositor-stages-before-draw` — ensures compositing completes before capture.

## Pitfalls

- **Snap Chromium cannot write to `/tmp`.** It fails with `No such file or directory` due to AppArmor confinement. Always write screenshots under `/home/ubuntu/` or a real user-writable path.
- **DBus/AppArmor warnings are noise.** Snap Chromium logs `org.freedesktop.DBus.Error.AccessDenied` and `org.freedesktop.UPower` errors. These are harmless; check for the `N bytes written to file` line to confirm success.
- **`file` command may not be installed.** Use Python `pathlib.Path(...).stat().st_size` to verify the screenshot file was created and has a non-trivial size.
- **Anchor hash for scroll position.** Append `#<section-id>` to the URL to screenshot below the fold (e.g. `#available-programs`).
- **This supplements, not replaces, build/test/curl verification.** Use it as visual QA after confirming HTTP 200 and deployed bundle markers.

## Verification sequence for deployed SPA changes

1. `curl` the public URL → HTTP 200.
2. `curl` the deployed JS bundle → grep for new copy/markers (e.g. `topNav.searchPrograms`).
3. Check for absent stale markers (e.g. `neon.tech` should not appear if local auth is intended).
4. Headless Chromium screenshot → `vision_analyze` for visual/responsive confirmation.
