---
name: preview-first-web-delivery
description: Safely implement and publish isolated web UI previews without changing production, including dirty-checkout handling, default-branch discovery, verification, and approval gates.
version: 1.0.0
metadata:
  hermes:
    tags: [web, preview, worktree, deployment, approval-gate]
---

# Preview-First Web Delivery

Use for material website UI changes that must be reviewed at a public preview before production integration.

## Workflow

1. Resolve the remote default branch from `refs/remotes/origin/HEAD`; inspect remote branches if it is absent. Never assume `main` versus `master`.
2. Fetch that branch with `git fetch --prune origin <branch>` and record `origin/<branch>`'s SHA. Do not use `git pull` for preflight.
3. Inspect `git status --porcelain`. Never stash, reset, overwrite, or build from a dirty shared/production checkout. If it is dirty, preserve it untouched and create a separate feature worktree directly from the fetched remote ref.
4. Implement only the requested UI scope in the isolated worktree. If the user requires a named coding model, probe the exact model and reasoning tier before launching the full task.
5. Run focused tests and the production build from the final workspace state. Keep unrelated baseline lint/full-suite failures separate from changed-file verification: report the full-suite totals and stack traces truthfully, then run feature-focused tests and changed-file lint without editing unrelated baseline code. When linting from a nested package directory, normalize Git's repository-relative paths first (for example, strip `apps/web/`) so a “no files matching” invocation error is not mistaken for lint evidence. If the feature altered shared query code, rerun the complete owning backend suite after focused regressions pass.
6. Build with the preview's actual public base path when the bundler supports a configurable base (for example, `VITE_BASE=/previews/<slug>/ npm run build`). Treat this preview-path build as fresh deployment evidence even if a prior production-base build passed.
7. Publish to a unique non-production directory. Use a clean-copy operation such as `rsync --delete` only against the exact preview directory. If the change depends on backend behavior, a frontend-only preview against the unchanged production API is not a working preview: run an isolated preview API on a separate port and a copied/sanitized database, proxy it under the preview namespace, and inject that preview API base into the SPA. Never edit or migrate production data for review.
8. Verify the preview end-to-end, not by HTTP status alone. Add explicit web-server locations for the SPA and any isolated preview API, with the preview's own SPA fallback and correct router basename/API base; otherwise production fallback can return HTTP 200 while React renders `Page not found`, or the UI can silently exercise old production backend behavior. Verify root and deep routes contain the preview HTML marker, public hashed JS/CSS have JavaScript/CSS MIME types, and the preview API returns JSON rather than SPA HTML. Then render the exact public URL in a real headless browser. Inspect rendered DOM or screenshot for expected content, assert `Page not found` and known runtime errors are absent, and check relevant console errors. Compare production asset hashes/state before and after to show production stayed unchanged.
9. Push the feature branch when required, report the commit and preview URL, and explicitly request approval. Do not treat a passing build, a positive comment, or silence as approval.
10. Merge and deploy production only after explicit approval. Remove rejected previews promptly and remove approved previews only after production verification succeeds.

For backend-dependent previews, follow `references/full-stack-isolated-preview.md` for the loopback API, copied database, Nginx proxy, build variables, and content-level verification pattern. For schema/API/UI changes in repositories with unrelated baseline failures, use `references/full-stack-verification-boundaries.md` to separate complete-suite, changed-file, focused-flow, preview transport, and browser evidence accurately.

When approval arrives but the shared production checkout contains unrelated work, follow `references/dirty-production-checkout-handoff.md`: rebase and verify in the clean feature worktree, update the remote production branch from that branch, build deployable artifacts there, and leave the dirty checkout untouched.

## Visual constraints

When asked to preserve the theme, treat tokens, palette, typography, surfaces, radii, shadows, and brand language as fixed. Create novelty through composition, hierarchy, grouping, spacing, responsive placement, and card scale. Add a focused structural or CSS assertion, but keep visual approval pending until the user reviews the rendered preview.

## Pitfalls

- Hard-coding `origin/main` in repositories whose default branch is `master`.
- Stopping because the shared checkout is dirty when an isolated worktree can safely start from the fetched remote ref.
- Building with the production base path and publishing under a preview subpath, which breaks asset URLs.
- Calling HTTP 200 on HTML sufficient; assets and deep-route fallback must also work.
- Claiming browser verification when only build/tests or HTTP probes ran. Report each boundary accurately.
