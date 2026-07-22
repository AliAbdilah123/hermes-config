# Timed resource capture in a small Go + React app

Use this pattern for user-triggered monitoring windows that must survive page reloads and expose progress.

## Minimal architecture

- Keep one mutex-protected capture manager in the backend.
- `POST` starts work asynchronously and returns `202`; reject overlap with `409`.
- `GET` returns running state, timestamps, progress, last error, and the latest completed result.
- Sample on a ticker and stop on a timer; tests inject short durations and a sampler rather than waiting for the production window.
- Aggregate by stable process identity available to the app (for example PID plus command). Divide totals by the whole capture sample count when ranking contribution over the complete window, so brief spikes do not look continuously active.
- Collect explicit `ps` columns (`pid=,pcpu=,pmem=,rss=,args=`) and treat the remaining fields as the command so arguments containing spaces are preserved.
- Persist only after successful completion. Write an indented JSON temporary file in the destination directory, `Sync`, close, then rename over the prior result atomically.
- Load the persisted result when the server starts so the UI shows the latest capture after reload.

## UI

- Disable the start button while running.
- Poll the status endpoint and show progress/end time.
- Keep the previous completed result visible while a new capture runs.
- Present separate top-CPU and top-memory tables with averages, peaks, RSS, and sample count.

## Verification

1. Run backend tests and build the binary; run the frontend production build.
2. Identify how the current backend is supervised **before** stopping it (`systemd`, process manager, shell parent, container). Restart through that supervisor. Do not assume killing the process causes an automatic restart.
3. Deploy generated frontend assets as one coherent build, removing stale hashed chunks.
4. Verify `GET` status, `POST` start, overlap rejection, and public HTML/hashed JS.
5. Let one real production-duration capture finish. Read back both the status API and persisted JSON; verify duration, sample count, and top-list limits.
6. Only then call the feature complete. A started capture is an in-progress verification, not final evidence.
