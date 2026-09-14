# Canonical Main Realignment with Live Deployment

Use when a project’s completed work is stranded on stacked task branches while `main` is stale and the same checkout backs a live systemd/nginx deployment.

## Safe sequence

1. **Inventory before changing refs**
   - Record `git status --short --branch`, remotes, all local/remote refs, graph, reflog, and worktrees.
   - Inspect nginx with `nginx -T` and systemd with `systemctl cat/show`; derive the exact static leaf, API `ExecStart`, working directory, environment file, database path, and localhost port.
   - Probe the current health endpoint before deployment.

2. **Preserve unfinished workspace state**
   - If the branch tip contains completed commits but the checkout also has a large uncommitted experiment, stash with untracked files and a dated descriptive message.
   - Run the project’s canonical tests first when practical. A failing dirty-tree test is evidence that the stash should remain quarantined, not work to fold into canonical main.

3. **Make main canonical without rewriting useful history**
   - Switch to `main` and merge the highest completed descendant branch with `--no-ff`; this absorbs its complete ancestor chain while leaving an explicit integration boundary.
   - Verify the graph and clean status immediately.
   - Do not delete integrated branch refs yet when another worktree, stash, or local-only repository still provides recovery value.

4. **Verify final main**
   - Run backend tests, frontend tests, typecheck, and production build from their actual module/package roots.
   - Treat the dirty-tree preflight failure separately from final-main evidence.

5. **Back up live state before replacement**
   - Create a timestamped backup outside the repository containing: SQLite backup, integrity result, environment file, current executable, static project leaf, systemd unit, and relevant nginx config.
   - Use SQLite’s backup API or native backup mechanism rather than copying a potentially active DB byte-for-byte.
   - Never print secret environment values in reports or logs. `systemctl cat/show` can expose credentials embedded in `Environment=` directives, so inspect service provenance through a redacting filter or report only environment key names. Treat unit files and copied environment files as secret-bearing artifacts and restrict backup permissions accordingly.
   - Do not parse SQLite integrity output by exact full-string equality unless headers are explicitly disabled: a user/global `.sqliterc` may enable column headers. Invoke `sqlite3 -noheader ... 'PRAGMA integrity_check;'` (or parse the final value) and require the value `ok`.

6. **Deploy exact runtime targets**
   - Build the binary to a temporary path, then install it over the exact systemd `ExecStart` path.
   - `rsync --delete` only into the discovered project leaf, never a shared `/projects/` ancestor.
   - Run `nginx -t`; skip nginx edits when the existing route is already canonical.
   - Restart the exact service and poll the real localhost health endpoint with a bounded retry.

7. **Verify all boundaries independently**
   - Require post-restart service active, expected health payload, and live DB integrity.
   - Verify local nginx HTML references the new asset, the exact asset returns JavaScript/CSS MIME, and the proxied API works.
   - Repeat HTML and API probes through the public origin. Browser-render E2E remains a separate gate when required.

8. **Handle the remote honestly**
   - A worktree `origin` pointing to another local checkout is not an upstream remote.
   - Confirm the exact hosted repository exists before adding/pushing. Repository names inferred from module paths are clues, not authorization to invent a destination.
   - If no exact remote exists, stop after local canonicalization/deployment and report the blocker. Do not create or push to a guessed repository.

## Multiple similarly named repositories

Treat similarly named checkouts as separate products until history and runtime evidence prove otherwise:

1. Compare root commits, module/package identity, remotes, and branch graphs. Unrelated root commits mean branch realignment must happen independently; never merge repositories merely because their names are similar.
2. Map each checkout to its own systemd `ExecStart`, environment/data directory, listener port, nginx route, static leaf, and database before changing either repository.
3. Canonicalize according to each repository's topology: merge the highest completed descendant into stale `main` with `--no-ff`; for a single linear repository still on `master`, rename that branch to `main` rather than manufacturing a merge.
4. Preserve dirty and untracked state separately in each repository. Stash messages should name the old branch and operation timestamp because a stash created before `master` → `main` retains the old branch label.
5. Verify API and frontend deployment boundaries independently. An nginx API-only route can be healthy while the corresponding SPA route correctly remains absent/404; do not invent a frontend route unless deployment intent requires one.
6. When a deployment sequence completes backups before a later build fails, retain and report that validated backup. Resume from the failed stage rather than recreating or overwriting it. Set an explicit module working directory for every build (or use the build tool's `-C` support) so multi-repository scripts do not accidentally build from a parent directory.
7. A test command that exits nonzero because no test files exist is not equivalent to failing tests. Report “no frontend tests present,” continue the independently required production build, and leave test scaffolding unchanged unless requested.

## Same-tip normalization and deployment scope

- If local `master` and canonical `main` should point to the same commit, do not manufacture an integration commit: create/rename `main`, verify the graph, then delete `master` only after checking worktree dependencies. When `origin/main` exists, fetch first, track it, and verify its exact SHA with `git ls-remote`; without a remote, report local-only canonicalization honestly.
- Match deployment scope to the product. A retained but explicitly unused backend may be tested as canonical source without being installed or assigned a service. For frontend-only products, back up and deploy only the static leaf and relevant nginx config.
- Attribute ambiguous listeners through PID → executable → cwd → cgroup/systemd unit; port proximity or nearby nginx blocks do not establish product ownership.
- If rebuilding changes a tracked executable, decide explicitly whether it is a versioned deployment artifact. Commit it only when repository convention already treats it that way; otherwise deploy from a temporary build path.
- Distinguish `clean` from `preserved`: intentionally retained untracked files still mean the worktree is not clean.

## Pitfalls

- Do not merge a large failing uncommitted refactor merely because it is newer than committed task work; preserve it separately.
- Do not call branch pruning “safe” merely because refs are ancestors of main. Keep refs needed by dirty linked worktrees, stashes, or local-only recovery until ownership is clear.
- Do not edit nginx when inspection proves its existing route, upstream port, alias, and SPA fallback already match the canonical deployment.
- A successful public HTTP probe is deployment evidence, not rendered browser E2E.
