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

1. Break the plan into workable, sequentially-ordered tasks.
2. Create each task in the kanban board with `hermes kanban --board <board> create`.
3. Only then begin dispatching and working tasks.

Do **not** start implementing before the kanban tasks exist. Do not create tasks after code is already written.

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

## Verification and reporting

- Use `runs`, `show`, and worker comments to verify whether a blocked task succeeded or failed.
- If a worker says tests passed, quote the command and status from the run/comment.
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
