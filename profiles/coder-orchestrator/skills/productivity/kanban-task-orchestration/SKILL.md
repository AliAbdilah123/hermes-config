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
