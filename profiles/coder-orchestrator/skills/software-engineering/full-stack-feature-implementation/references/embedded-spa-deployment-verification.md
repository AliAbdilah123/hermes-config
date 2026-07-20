# Embedded SPA deployment verification

Use when a backend executable embeds built frontend assets and the deployed UI still shows an older component after source changes.

## Root-cause test

Distinguish four states:

1. Frontend source contains the new UI.
2. Frontend `dist/` contains the new markers and excludes legacy markers.
3. The newly compiled backend binary embeds that exact bundle.
4. The running service uses that newly compiled binary at its configured runtime path.

A pass at an earlier state does not prove a later state.

## Focused Go regression test

For a Go `embed.FS`, read embedded `index.html`, extract its hashed JS filename, then read that asset and assert:

- New stable accessibility/copy markers are present, such as placeholder text and icon-button `aria-label`s.
- Legacy label/button strings are absent.

This catches stale copied assets and avoids coupling the test to a changing content hash. Prefer user-facing or accessibility strings over minified implementation details.

## Deployment sequence

1. Build the frontend into the directory consumed by `//go:embed`.
2. Run the focused embedded-asset test.
3. Compile the backend executable.
4. Inspect the service definition and deploy to its exact `ExecStart` path; do not assume the local build output is the runtime binary.
5. Restart the service and verify it stays active.
6. Fetch local and public HTML, resolve the served hashed JS asset, and inspect that served asset for the new and legacy markers.

## Common pitfall

Recompiling to a repository-root filename while systemd runs `bin/app` leaves production unchanged. Likewise, editing source after the frontend build leaves the backend embedding an old `dist/`. When production retains an old style despite correct source, investigate artifact lineage before editing the component again.
