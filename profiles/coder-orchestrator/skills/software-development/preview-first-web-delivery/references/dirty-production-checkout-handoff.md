# Deploying an approved preview when production checkout is dirty

Preserve unrelated work: never reset, stash, clean, or overwrite a shared production checkout merely to deploy an approved feature.

1. Discover and fetch the real production branch (`main` or `master`).
2. Rebase the clean approved feature worktree onto current `origin/<production-branch>`.
3. Remove generated preview artifacts (compiled binaries, copied databases) before rebase/commit; confirm they are not tracked.
4. Rerun focused backend/frontend regressions and the production build after the rebase.
5. Push the rebased feature branch, then update the remote production branch from that verified branch.
6. Build deployable API/frontend artifacts in the clean feature worktree—not the dirty production checkout.
7. Back up and atomically install the API binary; restart and verify service health.
8. Deploy frontend `dist/` with deletion of stale hashed assets, scoped only to the production document root.
9. Verify remote production SHA, HTML basename/API injection, JS/CSS MIME types, API JSON, service state, and Chromium-rendered DOM.
10. Stop/remove isolated preview processes and routes only after production verification succeeds.

This separates source-control integration and artifact deployment from unrelated local workspace state while ensuring production corresponds to the pushed revision.
