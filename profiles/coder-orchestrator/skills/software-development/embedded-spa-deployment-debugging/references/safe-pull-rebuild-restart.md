# Safe pull, rebuild, restart

Use when a systemd service runs a repository-built executable and the worktree is dirty.

1. Inspect `git status`, fetch, and compare the local diff with the incoming commit before pulling.
2. If local edits block a fast-forward, stash them with a descriptive name, then `git pull --ff-only`.
3. Compare the stash against the pulled tree. Textually different implementations may be semantically equivalent; inspect the diff rather than blindly applying or dropping it. Drop only when the upstream change fully supersedes the local intent.
4. Run the repository's tests, then rebuild the exact executable referenced by `systemctl cat <service>`; restarting an old binary does not deploy pulled source.
5. Restart the service and wait for its explicit readiness signal (journal line or bounded health-check retry). `systemctl is-active` immediately after restart proves process state, not socket readiness.
6. Verify both the local listener and the public endpoint. A root route may legitimately return 404, so use a known health/API route when available or confirm the expected status.
7. Finish with a clean/synced `git status`, service status, running log line, and public HTTP result.

Prefer bounded readiness polling over a fixed sleep for services with variable startup time.
