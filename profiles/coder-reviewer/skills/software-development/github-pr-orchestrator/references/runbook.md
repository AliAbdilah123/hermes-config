# GitHub PR Orchestrator Runbook

## Worker runbook (for worker-strong / worker-medium / worker-easy / reviewer)

When you are spawned by the dispatcher:
1. Read `HERMES_KANBAN_TASK` from env.
2. Read `HERMES_KANBAN_BOARD` from env (kanban DB path).
3. Use kanban toolset (`kanban_show`, `kanban_comment`, `kanban_complete`, `kanban_block`) only during task execution.

## Orchestrator runbook

When an idea/work-request arrives:
1. If not already a kanban task, create one with:
   - title
   - description = PRD summary + API contract links
   - complexity = low / medium / high
   - model = routed worker model
   - assignee = routed profile

## Complexity → profile mapping
- `high` -> `worker-strong`
- `medium` -> `worker-medium`
- `low` -> `worker-easy`
- `review` -> `reviewer`

## Git / GitHub workflow (each task)

Preferred commands:
- `git checkout -b kanban/<task_id>-<slug>`
- Make changes.
- `git add -A && git commit -m "<task_id>: <short description>" && git push -u origin HEAD`
- `gh pr create --fill`

Reviewer:
- Leave review comments or approve via GitHub PR review CLI.
- On approval, `gh pr merge --squash --delete-branch`

Merge gating:
- Do NOT merge until reviewer approves.
- If reviewer rejects, create follow-up task with `parents=[original_task_id]` and reassign to original assignee.

## Fallbacks
- If `gh` fails, report the failure in `kanban_comment` and block the task.
- If a branch already exists, append short random suffix and retry once.
