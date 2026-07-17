# Deploy → Verify → Commit/Push Gating

Use this for frontend changes that must be deployed and pushed in the same task.

## Safe sequence

1. Build from the frontend package directory.
2. Deploy from the repository root using the build artifact's **repository-relative path** (for example, `apps/web/dist/.`), or stay in the package directory consistently. Do not assume `dist/.` exists after changing working directories.
3. Run deployment and verification under `set -e` so a failed copy, asset lookup, or assertion stops the command immediately.
4. Verify the public index references the newly built asset hashes and each referenced asset returns 2xx.
5. Verify changed behavior with markers that distinguish the production component from prototypes, tests, or dead code.
6. Only after deployment verification succeeds: stage, commit, and push.

Prefer separate tool calls for:

- build;
- deploy + public verification;
- commit + push.

This prevents a successful later `git commit` or `git push` from masking an earlier failed deployment command in the same shell chain.

## Marker pitfall

A removed string may remain in the production bundle because a prototype, test fixture, or unused component still contains it. Therefore, broad bundle assertions such as `assert old_copy not in bundle` can be false negatives.

Use one or more of:

- deployed CSS markers scoped to the changed production class;
- DOM inspection or screenshot of the authenticated route;
- a new production-only class or accessible heading marker;
- source-map/module inspection when available.

Treat asset HTTP 200 plus scoped CSS/DOM evidence as stronger than an unscoped string-absence assertion.
