# Embedded frontend assets: stale running application triage

Use this when source and tests show a frontend feature exists, but the currently opened application does not display it.

## Diagnostic sequence

1. Confirm the feature exists in current source and that its required API fields are populated.
2. Inspect the HTML and hashed JS/CSS asset names served by the running application.
3. Build the frontend and compare the generated asset names/content with what the live process serves.
4. Compare the running process start time with the feature commit/build time.
5. Check whether the backend embeds generated frontend files at compile time (for Go, look for `//go:embed`). If so, rebuilding only the frontend is insufficient.
6. Run frontend tests/build and backend tests/build.
7. Rebuild the backend binary after regenerating embedded assets, restart the managed service, then verify readiness with a retrying HTTP probe.
8. Confirm the served HTML references the new asset hash. Only then suggest a browser hard refresh for client/CDN caching.

## Common root cause

A long-running backend binary contains an older snapshot of the frontend. The repository can be clean and current while the opened app remains stale because embedded files are captured at backend compile time.

## Operational pitfalls

- Run package-manager commands from the directory containing the relevant `package.json`; run backend commands from the backend module root.
- A service manager may report `active` before its HTTP listener is ready. Retry the health request briefly rather than treating the first connection refusal as deployment failure.
- Do not change working source merely because the live UI is stale. Establish source/build/runtime divergence first.
- Verify the exact live asset hash or content after restart; process status alone is not proof that the new frontend is served.
