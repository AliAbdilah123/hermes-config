# Nginx Application Inventory and Canonical-Branch Realignment

Use when asked to inventory and realign every nginx-backed application not already assigned.

## Fleet inventory

1. Treat `nginx -T` as the complete routing source, not directory names or running services alone. Extract every `server_name`, application `location`, `root`/`alias`, and `proxy_pass`.
2. Classify every route explicitly:
   - assigned application: excluded with the assignment name;
   - unassigned application: must be mapped and assessed;
   - preview, PRD, system utility, generic directory listing, or explicit retired/disabled route: excluded with evidence;
   - legacy route belonging to an assigned product: classify under that product rather than treating it as a separate app.
3. Reconcile nginx routes against static leaves, source checkouts, systemd provenance, and listening ports. A source directory or service without an nginx route is not nginx-backed; an nginx API proxy without a SPA block is an API-only deployment.
4. Do not invent a frontend route for an API-only application. Record that the generic catch-all returns 404 if that is the configured behavior.

## Repository identity

1. Run `git rev-parse --show-toplevel` from each apparent app directory. Several apps may be subdirectories of one legacy monorepo; do not mistake a subdirectory for an independent repository.
2. Capture status, refs, graph, remotes, reflog, and worktrees before changing branches.
3. For a standalone linear task-branch stack with no `main`, preserve dirty/untracked state, create `main` at the intended completed boundary, and use an explicit `--no-ff` integration commit when a lower completed branch is the canonical baseline. Verify the graph immediately.
4. If an app lives inside a shared monorepo, do not rename the repository branch or create an app-specific branch policy unless the whole repository is in scope. Report that branch canonicalization is constrained by repository ownership.
5. No remote means local canonicalization only. Never infer or create a destination from project names.

## Verification and deployment

- Run each repository's backend tests/build and frontend tests/build independently. A missing frontend route does not waive frontend build verification when frontend source exists and deployment is intended.
- Back up exact binaries, static leaves, service units, relevant nginx config, and live databases before replacement. Use SQLite's online backup API and integrity check.
- Deploy only exact runtime targets: install the built binary over the discovered `ExecStart`, and `rsync --delete` only to the application leaf.
- Restart only changed services. Do not edit nginx when the existing route is already canonical; still run `nginx -t`.
- Verify localhost and public boundaries separately: service state, health/API payload, HTML, referenced asset MIME, and expected 404 behavior for absent UI routes.

## Reporting invariant

Produce a no-route-skipped table or list. Every application-like nginx route must appear as realigned, already assigned, preview/system/non-app, retired, or blocked—with the evidence supporting that classification.
