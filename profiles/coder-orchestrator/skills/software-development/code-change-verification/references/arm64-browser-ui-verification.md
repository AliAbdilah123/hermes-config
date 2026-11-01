# ARM64 browser UI verification

Use when browser-click/screenshot verification is required on Linux ARM64 and the default Chrome-for-Testing installer cannot supply an ARM64 build.

## Workflow

1. Check for an existing system Chromium (`chromium-browser`, `chromium`, or `/snap/bin/chromium`) before installing another browser.
2. Prove the binary itself can load the public route:
   ```bash
   chromium-browser --headless=new --no-sandbox --disable-dev-shm-usage --dump-dom 'https://example.test/'
   ```
3. For `agent-browser`, point it at the system browser:
   ```bash
   export AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium-browser
   agent-browser open 'https://example.test/'
   ```
4. If the agent-browser daemon launches but hangs on snapshots, use `playwright-core` with `executablePath` set to the same system Chromium. Install it temporarily with `npm install --no-save playwright-core`, run the E2E script, then remove `node_modules` and `package-lock.json` so verification does not alter the project.
5. Assert behavior in the browser, not merely source markers. For asynchronous chat UI, cover:
   - draft state before first send;
   - loading indicator and disabled send control;
   - inline failure plus retry action;
   - history search and restored results.
6. Use route interception to deterministically exercise slow and failed network states without waiting for a real provider failure.
7. Save screenshots for each state and visually inspect them. Treat newly observed unrelated layout defects as separate findings; do not silently expand the approved implementation scope.

## Evidence standard

Record the exact public URL, browser assertions, screenshot paths, and whether failures were simulated through interception. API E2E is useful but does not replace browser evidence when visual states were explicitly requested.
