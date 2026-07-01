# Creating real Hermes Kanban tasks for project work

Use when the user asks to "use Kanban", "put this in Hermes Kanban", or says they cannot see tasks in the Hermes Kanban UI.

## Key lesson

The session `todo` tool is only an in-chat checklist. It does **not** create durable Hermes Kanban cards. For user-visible Kanban work, use the Hermes Kanban CLI/tooling and verify the board list.

## Minimal workflow

```bash
hermes kanban init
hermes kanban boards create <board-slug> --name "<Display Name>" --default-workdir /absolute/project/path || true
hermes kanban boards switch <board-slug>
hermes kanban --board <board-slug> create "Task title" \
  --body "Concrete completion criteria" \
  --workspace dir:/absolute/project/path \
  --assignee <profile> \
  --idempotency-key <stable-project-task-key> \
  --created-by <user-or-project>
hermes kanban --board <board-slug> list
```

## Dependency graph pattern

Create cards with stable idempotency keys, collect the returned task IDs, then link dependencies:

```bash
hermes kanban --board <board> link <parent_task_id> <child_task_id>
```

`link parent child` means the child depends on the parent.

## Pitfalls

- Do not tell the user Kanban is ready after only calling the session `todo` tool.
- Always run `hermes kanban --board <board> list` and report the real task IDs.
- If the gateway dispatcher is running, newly-created ready tasks may be claimed immediately. Avoid creating future/downstream tasks as ready unless that is intended; create/link quickly, or initially block/schedule downstream work and unblock/promote when dependencies are ready.
- Use idempotency keys so rerunning the setup does not duplicate cards.
- Use `--workspace dir:/absolute/path` for an existing repo when workers should operate in-place; use worktrees only when isolated branches are desired.
