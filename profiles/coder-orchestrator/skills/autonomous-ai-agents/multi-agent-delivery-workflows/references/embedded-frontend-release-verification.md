# Embedded frontend release verification

Use this pattern when a backend serves frontend assets embedded at compile time.

1. Run backend tests and frontend tests separately.
2. Run the frontend production build and confirm it copies the generated output into the backend embed directory.
3. Review the generated-asset diff: a hashed bundle rename plus the corresponding `index.html` reference change is expected; an unreferenced deletion is not.
4. Commit generated embedded assets when the repository tracks them.
5. Rebuild the backend executable after the frontend build. Restarting an old binary will continue serving the old embedded bundle.
6. Restart the service and verify it is active.
7. Fetch the public page and confirm both HTTP success and the new bundle hash (or another release-specific marker) in the returned HTML.
8. Report the canonical public domain, not a guessed development subpath.

For delegated coding agents, prohibit commit/push so the orchestrator can inspect generated files, run final tests, rebuild, deploy, verify, then commit and push as the delivery gate.