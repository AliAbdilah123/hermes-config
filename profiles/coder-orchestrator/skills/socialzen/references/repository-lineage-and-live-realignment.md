# Repository lineage and live realignment

Use when Scheduling-Post has multiple checkouts, feature branches, legacy product forks, or independently deployed services and the user asks to realign everything to the canonical branch.

## Inventory before integration

1. Enumerate every checkout whose `origin` resolves to the Scheduling-Post repository. Record branch, HEAD, upstream, dirty state, and `git worktree list --porcelain`.
2. Fetch/prune in each independent clone. Compare candidates against the remote default branch with ancestry, unique commits, and three-dot file diffs.
3. Inventory runtime identity separately with `systemctl cat/show`, listeners, nginx routes, document roots, executable paths, environment files, database paths, and public URLs.
4. Treat a shared Git remote as weak evidence of one product. Check package identity, backend architecture, database, service, port, and public route. A legacy Brand Organizer/content-factory lineage can remain a distinct deployed product even when it shares Scheduling-Post history with SocialZen.

## Canonical integration

- Create a clean integration worktree from the fetched remote default branch. Do not use dirty operational checkouts as the integration surface.
- Merge active sibling histories with normal merges when both contain useful, overlapping development. This preserves provenance and lets Git reconcile their shared ancestors.
- Do not merge old backup branches or product-port branches merely because they are unmerged. Inspect whether they are obsolete architecture, screenshots/plans, or a separately maintained deployed product.
- Preserve dirty databases, plans, docs, and agent workspace files. Never reset or clean unknown work during realignment.
- The local branch name and remote default branch name may differ. Push with an explicit refspec and verify the exact remote ref SHA (for example, local `main` to remote `master`).

## Verification and deployment boundaries

1. Install locked frontend dependencies in the clean worktree before classifying missing-module test/build output as product failure.
2. Run frontend tests, typecheck, and production build independently; run Go tests and an explicit binary build independently. Report baseline test failures precisely rather than hiding them behind successful builds.
3. Discover the exact systemd `ExecStart` binary and nginx document root. Back up the live SQLite database with SQLite's online `.backup`, verify the backup, back up the executable, replace the exact binary, deploy static files with `rsync --delete` only to the project leaf, restart, and poll health.
4. Build a prefix-mounted SPA with its real public base. A root-base build served under `/projects/socialzen/` can make asset requests hit a domain-root redirect and return HTML/302. Verify generated HTML paths, then require referenced JS/CSS to return the correct MIME type from both root and deep SPA routes.
5. A configured nginx route whose static directory is absent returns misleading `500`/fallback behavior while its API can remain healthy. Restore the missing leaf build independently; do not infer frontend health from backend health.
6. Verify source commit -> built index hash -> deployed index hash -> public HTML asset names -> public asset MIME -> local service health. Browser-render evidence remains a separate gate.

## Conservative cleanup

- Prune stale worktree metadata after integration.
- Remove only temporary clean worktrees created for the operation.
- Retain active feature worktrees, dirty checkouts, uncertain local branches, backup refs, and distinct-product branches unless their redundancy is proven and deletion is explicitly safe.
- Report which histories were integrated, which were intentionally kept distinct, and why.
