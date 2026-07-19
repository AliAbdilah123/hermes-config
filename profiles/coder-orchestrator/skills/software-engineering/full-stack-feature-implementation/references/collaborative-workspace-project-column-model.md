# Collaborative Workspace / Project / Board / Column Retrofit

Use when retrofitting collaboration into a small Go + SQLite + React/Vite app that already has owner-scoped Workspaces, Boards, Projects, and Columns.

## Domain invariants

- Workspace is the collaboration/access boundary.
- Project belongs to one Workspace and owns the execution directory.
- Board belongs directly to one Workspace only. Do not add or infer a Board-to-Project association.
- Column belongs to one Board and one Project; validate that both share the same Workspace.
- Preserve existing Column worktree fields and behavior when adding Project selection.
- Runtime execution uses the enabled worktree directory, otherwise the selected Project directory.

## Safe migration sequence

1. Add membership and invitation tables.
2. Backfill every legacy Workspace owner into membership as `owner`.
3. Create a deterministic Default Project from each legacy Workspace directory.
4. Add nullable `columns.project_id`, backfill it, then enforce required selection at the API boundary. Rebuild to `NOT NULL` only when safe.
5. Remove obsolete cardinality constraints that conflict with the new model:
   - `UNIQUE(user_id, root)` prevents multiple name-only Workspaces when roots are empty.
   - `UNIQUE(workspace_id)` on Boards prevents multiple Boards per Workspace.
6. SQLite table rebuilds must be atomic and restart-safe. Use one dedicated `sql.Conn` because `PRAGMA foreign_keys` is connection-local. Disable FKs on that connection before beginning, rebuild both tables in one transaction, run `pragma_foreign_key_check`, commit, restore FKs, and clean stale `_new` tables safely.
7. Test migration from the actual legacy schema, preserve IDs/data/FKs, reopen twice, and assert no `_new` tables remain.

## Authorization audit

Replace direct `resource.user_id = session_user` checks with shared Workspace membership checks across every Workspace, Project, Board, Column, member, and invitation path. Keep destructive/management operations owner-only where required. Search legacy endpoints too: an older `POST /projects` route can silently bypass the newer nested owner-authorized route.

Server-side guards:

- Cross-Workspace Project IDs are rejected for Columns.
- Final Workspace owner cannot be removed.
- Ordinary members can read/open Workspace Boards and Columns but cannot manage owner-only resources.
- APIs do not leak inaccessible record existence.

## Invitation safety

- Normalize email and validate at the mail trust boundary with `net/mail.ParseAddress`.
- Explicitly reject CR/LF, address lists, display-name forms, malformed input, and parsed mailbox mismatch before interpolating SMTP headers.
- Generate a random token; store only its hash.
- Keep acceptance transactional: verify active/unexpired/unaccepted invitation, claim it once, insert membership idempotently, check row counts and every error, then commit.
- Prevent duplicate unexpired active invitations while permitting reinvite after expiry. Delete/retire expired unaccepted rows transactionally before insertion; a uniqueness condition based only on `accepted_at IS NULL` permanently blocks expired recipients.
- Ensure the emailed URL exactly matches frontend parsing and is base-path aware (for example `BASE_URL/?invite=<escaped-token>`).
- Invitation failure must not turn an authenticated frontend session into a signed-out UI state.
- If mail transport is unavailable, report delivery failure honestly; never claim the invite was sent.

## Runtime directory safety

Creation-time validation is insufficient because paths and symlinks can change. Immediately before job state/run mutation:

1. Load the selected Project directory or enabled worktree path from the database; fail closed on query/empty result.
2. Re-run canonical path containment, existence, directory, and readability checks under `WORKSPACE_ROOT`.
3. Execute using the resolved real path (the canonical helper's resolved return), not the lexical absolute path. This narrows symlink-retarget TOCTOU exposure.
4. If validation fails, do not increment attempts, create a run, or transition to in-progress.

Test missing/deleted directories and symlinks retargeted outside the root.

## Frontend integration checklist

- Native avatar `<details>` closes on outside pointer and before every menu action.
- Workspace create asks only for Name.
- Workspace detail tabs: Info, Projects, Boards, Users.
- Boards tab lists Workspace Boards with Column counts and Open actions; no Project field.
- Column create/edit adds required Project select while preserving Git worktree toggle and Worktree name.
- No-Project state disables Column submission and links to Projects.
- Native History helpers must cover initial parse, push/replace, `popstate`, back actions, tab changes, avatar Workspaces action, and Open Board. A state-only `setView` creates refresh/back divergence.
- Invitation query survives sign-in/sign-up and resumes acceptance.

## Verification gates

- Focused RED/GREEN tests for each boundary.
- Full Go tests, vet, build.
- Frontend tests, TypeScript, production build, embedded-asset rebuild.
- Independent review should explicitly inspect legacy routes, migrations from old schema, authorization breadth, invitation URL/transactions, and runtime path revalidation.
- Deploy only after service restart/migration succeeds; readiness may lag systemd's `active` transition, so retry the HTTP health probe briefly.
- Verify public index references the new asset hash, assets return 200, authenticated API returns 401 when logged out, and bundle contains feature markers.
