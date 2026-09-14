# Fleet-wide Git realignment and deployment

Use when asked to reconcile every nginx-backed application onto its canonical branch, rebuild, deploy, and prune stale Git state.

## Workflow

1. Inventory applications from the effective config (`nginx -T`), not directory names. Record each named route/domain, static root or alias, proxy port, and whether it is production, preview, infrastructure, or retired.
2. Map each route to its exact source repository and runtime unit/command. Group multiple worktrees sharing an origin, but do not conflate distinct products merely because they share repository ancestry.
3. Work in bounded parallel batches (normally one worker per repository family). Give every worker the route, source paths, remote, static root, proxy port, and preservation rules.
4. Before changing Git, inventory status, stashes, local/remote refs, and worktrees. Preserve `.env`, databases/WALs, uploads, runtime binaries, untracked documents, and ambiguous dirty work.
5. Fetch and identify the actual canonical lineage. Use `main` when requested, but report separately when a hosted repository still declares another default branch or requires admin permission to change it.
6. Merge unique useful branches with normal `--no-ff` merges and semantic conflict resolution. Do not merge overlapping experiments blindly. Keep uncertain refs/worktrees until feature-specific reconciliation proves them integrated.
7. Prune only clean worktrees and branches proven fully contained or otherwise equivalent. A backup checkout or stash is not disposable merely because production builds.
8. Run repository-native tests and builds from the correct package/module roots. Record baseline failures literally; a successful build does not make a red suite green.
9. Discover deployment truth from nginx, listeners/processes, and systemd. Back up the runtime database and old binary/static leaf, integrity-check SQLite, rebuild the exact executable, deploy static output with leaf-scoped `rsync --delete`, restart or otherwise refresh the real runtime, and poll readiness.
10. Push the canonical branch only to an evidenced remote and verify with `ls-remote`. Never invent a destination for a local-only repository.
11. Independently run a fleet gate after all workers finish: `nginx -t`, current branch/SHA/remote status, expected service or listener health, public HTML/API responses, referenced asset MIME types, and source-build versus deployed hashes where practical.

## Delegation result discipline

- A worker's `completed` envelope is not proof its task succeeded; inspect the actual summary for provider errors, missing SHA/push/deploy fields, or partial side effects and retry or repair.
- Worker summaries are self-reports. Independently verify omitted metadata and every critical runtime boundary.
- Do not infer a service failure solely from a guessed unit name. If the unit is absent, inspect the configured proxy port and owning process; classify unmanaged/alternate supervision accurately.
- Conversely, a running listener is not durable supervision. Report when no unit exists instead of claiming `systemctl` health.
- API health paths vary. Confirm the repository/nginx contract before treating a `404` at a guessed `/health` endpoint as failure.

## Completion reporting

Separate projects into:

- pushed and deployed canonical branches;
- canonicalized/deployed local-only repositories with no evidenced remote;
- preserved divergent or dirty work requiring semantic follow-up;
- administrative blockers such as hosted default-branch permissions;
- non-green tests and missing authenticated public E2E.

Call the fleet deployed/reachable when transport and runtime gates pass, but reserve `READY` for projects whose required authenticated public E2E passed.