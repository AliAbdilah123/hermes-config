# Preview-first worktree approval gate

Use this workflow when a website change requires review before production deployment.

## Lifecycle

1. Start from an up-to-date production branch and require a clean baseline.
2. Create a dedicated feature branch and isolated Git worktree. Keep the primary checkout, production branch, and live production assets unchanged.
3. Implement and verify inside the worktree. Build from the feature worktree or its clean commit—not from a dirty primary checkout.
4. Publish the build to a separate, clearly named public preview path or hostname. Record the preview directory, URL, branch, and commit.
5. Apply review revisions only to the feature worktree and preview deployment.
6. Treat preview availability, positive comments, and requests for another revision as non-approval. Merge/deploy only after an explicit approval statement authorizing production implementation.
7. After approval, run final tests/build, squash-merge into the production branch, push, deploy the production artifact, and verify the public production route in a browser plus asset/API health checks.
8. Remove the preview only after production verification succeeds. Remove its route/assets/worktree/branch as appropriate, then verify production again.
9. If the user says “not approved,” “reject,” or otherwise explicitly rejects the preview, immediately remove the public preview and associated temporary deployment. Keep production unchanged. Preserve or delete the feature branch/worktree according to the user’s wording; do not merge it.

## Approval semantics

A public preview is evidence for review, not authorization for release. The approval gate must be explicit and applies independently to:

- merging or squash-merging;
- pushing the production branch;
- copying assets into the production document root;
- restarting or replacing production services;
- deleting the preview after a successful release.

If wording is ambiguous, leave production unchanged and ask whether the user approves production deployment.

## Preview isolation checklist

- Distinct worktree and feature branch
- Distinct preview URL and deployment directory
- No writes to production document root
- No merge/push to production branch
- No production service restart
- Preview URL returns the intended feature artifact
- Production URL still serves the pre-change artifact

## Cleanup checklist

- Remove preview nginx route or static alias if dedicated
- Remove preview deployment directory
- Validate and reload nginx when configuration changed
- Remove/prune worktree
- Delete temporary branch only when approved by policy/user intent
- Confirm preview no longer serves the isolated build
- Confirm production remains healthy
