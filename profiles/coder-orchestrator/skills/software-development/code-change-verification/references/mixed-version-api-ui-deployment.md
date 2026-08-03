# Mixed-version API/UI deployment verification

Use when a frontend and backend change an API response shape, especially when static SPA assets and a separately compiled service are deployed independently.

## Failure pattern

A component test can pass while the public form is empty because it injects the desired prop directly. In production, the frontend may expect a new field such as `summary` while the running backend still returns the legacy field such as `points`. A fallback like `preview?.summary ?? ""` hides the contract mismatch as an empty control.

## Required workflow

1. Test at the API-consumption boundary, not only the leaf component:
   - Feed the current response shape through the real normalization/state-setting path.
   - Feed the legacy response shape through the same path when rolling deployments or stale binaries are possible.
   - Assert the rendered control is non-empty and prefilled.
2. Normalize during compatibility windows:
   - Prefer the current field.
   - Convert the legacy field deterministically.
   - Keep the adapter small and remove it only after old producers cannot exist.
3. Trace deployment as separate artifacts:
   - source commit;
   - generated frontend bundle;
   - compiled backend binary;
   - running process;
   - public HTML/JS and public API response.
4. Rebuild the exact executable named by systemd and restart the service. A frontend build or Git push does not update a compiled backend.
5. Verify the public API response shape and the authenticated rendered form. Asset strings and HTTP 200 are supporting evidence only.
6. Report `implemented and deployed; authenticated public E2E pending` unless the exact authenticated flow was exercised. Do not call the work completed or present the public link as completed evidence before that gate.

## Safe verification in a dirty shared checkout

If unrelated edits exist in test or source files, do not append to, restore, or stage them. Put the compatibility test in a separate focused test file, commit only explicit task paths, and build/deploy from a clean worktree at the immutable task commit.

When a broad SQLite-backed Go suite flakes due to cleanup/locking, rerun the exact failed test at the immutable commit to classify it. Do not turn targeted reruns into a claim that the broad suite passed.
