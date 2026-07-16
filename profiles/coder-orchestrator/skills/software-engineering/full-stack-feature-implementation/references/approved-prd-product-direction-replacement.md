# Implementing an Approved PRD That Replaces the Existing Product Direction

Use this when an approved PRD targets an existing repository but defines a materially different product architecture or domain.

## Workflow

1. Read the canonical PRD and extract required stack, domain entities, API surface, state rules, acceptance criteria, and explicit deferrals.
2. Inspect the repository before editing:
   - current architecture and entrypoints
   - git branch/status/remotes
   - tests/build commands
   - deploy/runtime configuration
   - installed runtime capabilities relevant to the PRD
3. Classify existing code into:
   - **preserve**: reusable mechanics such as Go module setup, SQLite driver/pragmas, `net/http`, safe `os/exec` argument handling, or test conventions
   - **replace**: incompatible domain models, provider abstractions, gateways, tools, or config systems explicitly deferred by the new PRD
   - **add**: missing vertical product slices
4. Treat the approved PRD as the scope boundary. Do not retain obsolete subsystems merely because they already exist, and do not add deferred compatibility layers.
5. Create or reuse visible Kanban tracking before implementation. For one tightly-coupled replacement in a shared worktree, one parent implementation card can be safer than prematurely parallel cards; keep a local checklist for acceptance slices.
6. Implement the thinnest complete vertical product, preserving only mechanics that shorten the work without distorting the new model.
7. Verify every PRD acceptance class with real output: backend tests/build, frontend tests/build, isolation/security smoke, concurrency/execution smoke, and deployed public behavior when deployment is authorized.
8. Commit and push only after verification. If the repository has no remote, commit locally and report that push is blocked rather than inventing a destination.

## Pitfalls

- **Repository identity is not architecture preservation.** Preserve the repository and history, but replacing incompatible application code is correct when the approved PRD explicitly changes product direction.
- **Do not turn tool availability into architecture drift.** Missing optional delegates should appear as unavailable in product behavior; they do not justify stubbing or removing the required availability model.
- **Do not report implementation as complete while a background worker is still running.** Say it is in progress, then verify the worker's edits, tests, deployment, and git state in the parent before claiming delivery.
- **A single broad worker claim is not verification.** The parent must inspect the diff and run the acceptance commands itself before deployment or final reporting.
