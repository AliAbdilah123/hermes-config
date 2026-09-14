# Canonical-main realignment

Use when a repository, duplicate checkout, remote branches, and a live deployment may represent different histories or artifacts.

## Inventory before changing anything

1. In every known checkout, fetch with pruning and record:
   - `git status --short --branch`
   - remotes and `HEAD`/tracked-default SHA
   - worktrees
   - local and remote refs
   - a decorated all-refs graph
2. Compare each branch to `origin/main` with ancestry counts, `git cherry`, and a diff/stat. Do not treat every non-merged branch as useful work: it may be an obsolete alternative architecture or a superseded implementation.
3. Hash or compare untracked files across duplicate checkouts. Preserve runtime databases, backups, environment files, and agent guidance unless explicitly authorized to remove them.
4. Discover the live artifact chain independently from Git:
   - systemd `WorkingDirectory`, `EnvironmentFile`, and exact `ExecStart`
   - runtime database path from effective service environment
   - nginx static document root and API proxy
   - public canonical and compatibility URLs

## Choose canonical history

- If the primary checkout and remote default branch already match, do not manufacture a merge or commit.
- Fast-forward stale duplicate checkouts only when tracked files are clean; untracked files do not prevent a safe fast-forward but still must be preserved.
- Delete remote branches only when they are fully merged into canonical main. Preserve divergent branches unless their obsolescence and removal are explicitly established.
- Verify the immutable local SHA equals the remote default-branch SHA after pushing.

## Deploy canonical artifacts

1. Run backend tests and the production frontend build from their actual module/package roots.
2. Before replacing runtime artifacts, create a timestamped backup outside the repository containing:
   - SQLite `.backup` output followed by `PRAGMA integrity_check`
   - current service executable
   - current static document root
3. Build directly to the exact executable named by systemd.
4. Replace only the contents of the discovered static document root; never delete the root or adjacent project directories.
5. Restart the service and poll its real local health endpoint with a bounded retry. An initial connection refusal immediately after restart is a readiness race if polling converges.
6. Prove the running `/proc/<pid>/exe` hash matches the rebuilt executable.

## Public verification

Verify separately:

- local API health
- public API health on every supported mount
- public HTML names the expected generated assets
- exact JS/CSS assets return correct MIME types and non-trivial bodies
- browser rendering contains stable product controls/content

A headless browser may emit GPU, D-Bus, accessibility-bus, or push-service host warnings while producing a valid DOM. Capture exit status, DOM/artifact size, page/runtime errors, and host warnings separately. Authentication-free landing-page rendering is not authenticated E2E; report that boundary explicitly.

## Completion report

Include canonical SHA, preserved divergent refs and untracked/runtime files, deleted merged refs, test/build results, backup path, service state, executable hash match, public URLs checked, and the strongest browser/E2E boundary actually proven.
