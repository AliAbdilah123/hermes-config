# Canonical branch realignment

Use when a repository has a stale primary checkout, many feature/preview worktrees, divergent local branches, or a deployment built from an unclear ref.

## Establish canon before changing refs

1. Fetch and prune, then record `origin/HEAD`, the remote default branch, protected-branch settings when accessible, local tracking branches, and the branch currently represented by production.
2. Treat words such as “main,” “master,” “production,” and “canonical” as potentially different identifiers. Do not create a new `main` merely because the request uses “main” if the remote default is `master`; either confirm the intended rename/cutover or realign the existing default branch.
3. Tie the live artifact to a commit when possible (build metadata, embedded marker, binary hash/build info, or deployment record). Service health alone does not identify source provenance.

## Preserve without promoting

1. Inventory every worktree with branch, HEAD, upstream, porcelain status, and runtime-only artifacts.
2. Preserve meaningful dirty work on its existing topic branch or in a patch/bundle. Do not create a broad “accumulated changes” commit containing unrelated plans, docs, product code, and tests just to make a checkout clean.
3. Never infer that every unique remote patch is approved or compatible. Build a patch-equivalence/ancestry table, then classify each branch as already integrated, approved for integration, superseded, unreviewed, or dirty/preserved.
4. Merge or cherry-pick only approved coherent ranges. Repeated conflict density is a scope signal: abort, preserve, and request a product decision rather than auto-merging a subset and calling the repository realigned.

## Verification and deployment gate

1. Create a clean integration worktree from the confirmed canonical remote tip. When the repository has only one clean worktree, the intended canonical branch is an ancestor of the current feature/default branch, and that feature contains the complete approved live application, checking out the canonical branch and making an explicit `--no-ff` merge is sufficient; do not manufacture another worktree or cherry-pick series. Record the topology first and preserve the merge commit as the canonicalization boundary.
2. Run every canonical check represented by the repository, including separate frontend tests/build and backend tests when both package manifests and backend modules exist. Run these against the exact integration commit before pushing or deploying. Reproduce claimed baseline failures at the untouched canonical baseline before classifying them as pre-existing.
3. Do not deploy a newly assembled integration when broad tests or lint fail unless the user explicitly accepts the named failures and deployment risk. A successful compile/build is not equivalent to a releasable tree.
4. Before creating or pushing a replacement primary branch, preflight permission to change the remote default branch (and branch protection when applicable). A credential that can push may still lack repository-administration permission. If the cutover cannot be completed, stop before deployment or explicitly report a staged candidate branch—not a canonical realignment.
5. Push the exact verified commit to the intended canonical branch, change the remote default branch/protection as the same cutover operation, then verify both the hosting API and `git ls-remote --symref origin HEAD` resolve to it. Update local `origin/HEAD` only after the remote symbolic HEAD changes; `git remote set-head origin -a` cannot perform the server-side cutover.
6. Deploy that immutable commit only after the canonical cutover succeeds, unless the user explicitly accepts deploying a candidate branch while the remote default remains elsewhere. Determine frontend and backend obligations independently: an nginx API proxy without a listening process is evidence of a missing runtime, while backend-looking source without a proxy or service is not by itself a deployment requirement. Before installing or replacing a service, preserve its database/uploads and record its current unit/process provenance. For Node services, resolve the exact executable used by the verified shell (`command -v node` plus `readlink -f`), record `node --version`, and use that absolute executable in `ExecStart`; systemd's `/usr/bin/node` may differ from the interactive runtime and lack required built-ins. After `daemon-reload`, require the unit to stay active, the expected port to listen, and a direct localhost API probe to pass before testing through nginx. For a static-only project, first prove nginx has no project API proxy and no matching service, then deploy only the frontend artifact; do not invent a backend deployment obligation from boilerplate backend files. Verify source `dist/index.html` and the served copy have identical hashes, extract the public asset URLs from live HTML, and require correct JS/CSS MIME types.
7. For public render evidence, use a real browser when available. If an automation daemon is unavailable but system Chromium exists, run headless Chromium directly with a unique cache-buster and `--dump-dom`; require expected title/content plus no `Uncaught`, `net::ERR`, or console-error markers. A missing screenshot does not invalidate a successful DOM render, but report browser-visible evidence as DOM/render evidence rather than screenshot evidence.

## Cleanup

Delete only clean worktrees and refs whose commits are proven contained or patch-equivalent and whose review/deployment role has ended. Preserve dirty/runtime-bearing worktrees. Report them as preserved—not pruned and not integrated.

## Required report

State: confirmed canonical branch and remote default; canonical SHA; source and live deployment provenance; integrated approved ranges; preserved/unreviewed branches; verification failures; deployment decision; and cleanup performed.