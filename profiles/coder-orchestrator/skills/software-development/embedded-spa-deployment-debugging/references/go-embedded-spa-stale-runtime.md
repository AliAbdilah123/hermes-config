# Go-Embedded SPA: Source Updated but Runtime Still Shows Old UI

## Symptom

A frontend change is committed and generated web assets may be current, but the running app and public URL still render the previous UI.

## Root cause pattern

A Go service using `//go:embed` captures generated frontend files when the Go binary is compiled. Building the frontend only updates files on disk; restarting an older binary keeps serving its embedded asset snapshot.

## Evidence-first diagnosis

1. Identify the asset filename referenced by the generated embedded `index.html`.
2. Compare it with the asset filename served by the local service and public URL.
3. Compare the binary modification time with the frontend change/build time.
4. Confirm systemd's exact `ExecStart` binary path.
5. Check current and served bundles for a unique marker from the changed UI.

A newer generated asset plus an older served asset isolates a stale embedded binary.

## Correct deployment order

Run commands from the directory containing the relevant manifest/module:

1. Build the frontend from its app directory; remove stale hashed assets before copying into the embed directory.
2. Build the actual Go entrypoint from the repository root, e.g. `go build -o bin/app ./cmd/app`; do not assume the root package is executable.
3. Restart the service running that binary and verify it remains active.
4. Compare local and public HTML asset filenames with a cache-busting query parameter.
5. Verify the new bundle marker or rendered behavior, not merely HTTP 200.

## Common false fixes

- Restarting without recompiling Go.
- Compiling Go before rebuilding/copying frontend assets.
- Inspecting source/generated files but not the served asset.
- Running `go build .` when `main` lives under `cmd/<app>`.
- Assuming a pushed commit changed the live binary.

## Minimal verification

Local and public HTML should reference the same newly generated hash. Then verify the actual requirement, such as truncated visible text and a copy control that copies the full underlying value.
