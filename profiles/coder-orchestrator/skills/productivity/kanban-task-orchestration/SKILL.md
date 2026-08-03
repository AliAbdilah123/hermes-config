---
name: kanban-task-orchestration
description: "Operate Hermes kanban task boards: inspect task state, advance dependency chains, handle review gates, and report status without unnecessary confirmations."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [kanban, task-orchestration, workflow, hermes]
    related_skills: [systematic-debugging, test-driven-development]
---

# Kanban Task Orchestration

## When to use

Use when the user asks about, starts, advances, unblocks, reviews, or audits tasks in a Hermes kanban board.

## Core workflow

1. Inspect current board state before acting:
   ```bash
   hermes kanban --board <board> list
   hermes kanban --board <board> show <task_id>
   hermes kanban --board <board> runs <task_id>
   ```
2. Distinguish blocked meanings:
   - `review-required` after a successful worker run usually means a handoff/review gate, not failure.
   - Dependency tasks may be blocked/todo because parents are not done.
   - Earlier mistaken auto-claims can leave final/report tasks blocked until their dependency chain is complete.
3. If the user has already approved the plan and says to proceed, complete intermediate `review-required` tasks that have passed verification, then dispatch the next task:
   ```bash
   hermes kanban --board <board> complete <task_id> --result '<concise result>'
   hermes kanban --board <board> dispatch
   ```
4. Continue the dependency chain without asking for per-task confirmation unless the user explicitly requests intermediate review.
5. Report the active next task and evidence from real command output.

## User-preference pitfall

For this user, do **not** require confirmations between individual kanban tasks once the plan has been reviewed. They review before tasks start and review after all tasks are done only. Treat intermediate `review-required` blocks as stale worker behavior unless there is an actual failure, destructive operation, or explicit stop condition.

## User-required workflow: break down first, then create kanban cards

When the user says "implement with kanban", the required sequence is:

1. Inspect the board first. If tasks already exist (for example from an earlier kickoff or dispatcher run), reuse and advance them instead of creating duplicates:
   ```bash
   hermes kanban --board <board> list
   hermes kanban --board <board> show <task_id>
   ```
2. If no suitable tasks exist, break the plan into workable, sequentially-ordered tasks.
3. Create each task in the kanban board with `hermes kanban --board <board> create`.
4. Only then begin dispatching and working tasks.

Do **not** start implementing before the kanban tasks exist. Do not create tasks after code is already written. Do not duplicate an existing board plan just because the user says "go ahead" after reviewing a PRD; first check whether the plan/tasks were already created.

## Shared-workspace parallel-task pitfall (CRITICAL)

When tasks share a workspace (`dir:` or `worktree`), the auto-dispatcher can claim and run them in parallel, causing file conflicts (two workers editing the same files simultaneously).

**The fix:** Always create dependent tasks with `--initial-status blocked` to prevent premature parallel execution on shared workspaces. After creating all tasks, link parent-child dependencies, then unblock tasks in sequence so each runs only after its parent completes.

```bash
# BAD — creates race: tasks get claimed in parallel before linking
hermes kanban --board $B create "Task 1" ...           # created as ready
hermes kanban --board $B create "Task 2" ...           # also ready — runs in parallel!
hermes kanban --board $B link task1 task2              # too late, both already running

# GOOD — prevents race
hermes kanban --board $B create "Task 1" ...           # ready — runs first
hermes kanban --board $B create "Task 2" ... --initial-status blocked  # blocked until linked
hermes kanban --board $B link task1 task2              # dependency established
# Task 2 stays blocked until Task 1 completes, then dispatcher promotes it
```

If tasks were already created as ready and the dispatcher claimed them in parallel, use `reclaim` and `unblock` to reset them after completing the parent.

## Recovering apparently stuck API-backed jobs

Do not classify a job as orphaned from `ps` output alone. A run recorded as `hermes-api:<session-id>` is remote/API-backed, not a local tmux process.

1. Read the latest job/run pair and resolve the workspace's persisted Hermes URL and API key.
2. Query both `/api/sessions/<session-id>` and `/api/sessions/<session-id>/messages`.
3. Classify before acting:
   - active session, no terminal assistant response → restore/reattach the watcher; do not retry;
   - terminal assistant response present, even if session metadata still has `ended_at: null` → treat the message stream as stronger completion evidence, ingest that exact response, and finish the existing run;
   - ended session with final response → persist it and finish the existing run;
   - missing/ended without response → block consistently and retry as a new attempt;
   - implementation commits landed while result collection was interrupted → match commits to jobs and run fresh required verification before repairing state.
4. A terminal assistant response means the latest message is an assistant message with substantive content and no pending tool calls. Do not infer completion from commit existence alone.
5. For manual SQLite recovery, use `.backup` first, then atomically update both `job_runs` and `jobs` and append timeline events. Never merely flip a stale row to `running`.
6. After a service restart, verify startup reconciliation processes every active API-backed run, including implementation-phase runs approved immediately before restart. It must inspect both session metadata and messages: reattach genuinely active sessions, but ingest terminal responses that arrived while the watcher was down.
7. Restarting the service is a diagnostic, not a recovery claim. Re-query both `jobs` and `job_runs` afterward; if they remain `in_progress`/`running`, startup reconciliation is still broken and another restart will not repair them.

See `references/api-backed-job-session-recovery.md` for a compact diagnosis and recovery recipe.

## Approval must enqueue before agent execution

For review-gated sequential job systems, treat “Approve implementation” as queue admission, not immediate agent execution:

1. The approval transaction moves the job from `in_review/review` to `todo/implementation` at the end of its lane and stores any approval reply for later delivery.
2. Approval must not contact the agent/provider, reopen the completed run, increment attempts, or mark the job `in_progress`.
3. The queue processor alone claims the job, atomically changes `todo → in_progress`, reopens/reuses the latest valid session/run, clears the pending approval payload, and sends the implementation prompt.
4. Keep duplicate approval idempotent: no duplicate approval/comment events and no duplicate provider dispatch.
5. Test both lifecycle halves with the lane paused or blocked for enqueue assertions, then unpause and invoke the real scheduler. Assert no provider request before claim and exactly one request after claim.
6. Preserve review-feedback/retry semantics separately; do not route implementation approval through a generic feedback-resume path unless the pending payload has an explicit durable discriminator.

This distinction keeps the board truthful: `todo` means queued, while `in_progress` means an agent is actively executing.

## Verification and reporting

- When a task session appears mixed with another session, trace the exact job → run → agent-session relationship and inspect the original remote message list before concluding contamination. Classify it as cross-task contamination, same-task execution drift, multi-attempt timeline confusion, or insufficient evidence. See `references/task-run-conversation-attribution.md`.
- Use `runs`, `show`, and worker comments to verify whether a blocked task succeeded or failed.
- If a worker says tests passed, quote the command and status from the run/comment.
- For Go projects, complete kanban implementation cards only after a real `go test ./...` and `go build` (usually `go build -o bin/<name> ./cmd/<name>`). If tests fail because other ready/running workers edited the same workspace, inspect the failing files and board state before retrying.
- Final updates after feature/fix work should include the project public link when known.

## CLI syntax pitfall

`--board` is a global option for `hermes kanban`, so place it before the subcommand:

```bash
hermes kanban --board <board> create "Task title" --body "..." --assignee <profile>
hermes kanban --board <board> list
hermes kanban --board <board> complete <task_id> --result "..."
```

Do **not** run `hermes kanban create --board ...`; argparse treats `--board` as an unrecognized subcommand argument.

## Safety boundaries

Do not skip explicit confirmation for destructive production deploy/copy operations if the user has not already authorized that class of action. Completing kanban review gates is not the same as deploying to production.
