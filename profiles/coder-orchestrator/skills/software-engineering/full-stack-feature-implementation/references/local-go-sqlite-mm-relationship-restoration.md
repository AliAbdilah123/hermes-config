# Restoring M:M relationships in local Go + SQLite migrations

Use when a migrated Go + SQLite API flattened an old many-to-many relationship into a single nullable FK (for example `tasks.goal_id`) but the source app supported arrays/junction rows (for example task `goalIds`).

## Pattern

1. **Preserve compatibility while adding the real model**
   - Add a junction table with a composite primary key and FK cascades:
     ```sql
     create table if not exists task_goals (
       task_id text not null references tasks(id) on delete cascade,
       goal_id text not null references goals(id) on delete cascade,
       primary key (task_id, goal_id)
     );
     create index if not exists idx_task_goals_goal_id on task_goals(goal_id);
     ```
   - Backfill from the flattened FK:
     ```sql
     insert or ignore into task_goals(task_id, goal_id)
     select id, goal_id from tasks where goal_id is not null;
     ```
   - Keep the legacy FK column temporarily for backwards-compatible clients (`goal_id` = first/primary goal).

2. **Read through the junction table**
   - Goal detail/list task counts should join through the junction:
     ```sql
     select count(*), coalesce(sum(case when t.status='completed' then 1 else 0 end),0)
     from tasks t join task_goals tg on t.id=tg.task_id
     where tg.goal_id=? and t.user_id=?;
     ```
   - Goal task lists should also join through `task_goals`.
   - Task list/detail responses should include both:
     - `goal_id` for old frontend compatibility
     - `goalIds: []string` from the junction table for restored M:M parity

3. **Write through the junction table**
   - When creating a task, insert every provided `goalIds[]` row into the junction table. Also wrap the returned task with `addGoalIDs()` so the create response includes the array.
   - When updating a task with `goalIds[]`, **delete existing rows first, then re-insert**. A plain `insert or ignore` on update leaves stale rows from the previous set:
     ```go
     s.db.Exec(`delete from task_goals where task_id=?`, id)
     for _, raw := range arr {
         if gid := fmt.Sprint(raw); gid != "" {
             s.db.Exec(`insert or ignore into task_goals(task_id, goal_id) values(?,?)`, id, gid)
         }
     }
     ```
   - When receiving a single `goalId`/legacy `goal_id`, also insert it into the junction table.
   - When linking existing tasks to a goal (`existingTaskIds`, `selectedTaskIds`, `/goals/:id/tasks`), `insert or ignore` into the junction instead of overwriting `tasks.goal_id`.
   - Only set `tasks.goal_id = coalesce(goal_id, ?)` to preserve a primary/backcompat goal without destroying existing relationships.
   - **Also fix `getTask`**: the single-task read path (used by update responses) needs the same `addGoalIDs()` enrichment that `listTasks` already has. Without it, the update response won't include `goalIds`.

4. **Avoid SQLite nested-query traps**
   - If the Go SQLite driver/service is configured with one open connection, collect rows, close them, then enrich with a second query. Do not run a junction-table query while the original `Rows` is still open.

5. **Verification checklist**
   - DB row count matches existing non-null FK rows after backfill.
   - `/api/tasks` returns `goalIds` arrays.
   - `/api/goals` and `/api/goals/:id` return tasks via the junction table.
   - Existing homepage/goal views still work because `goal_id` remains present.
   - Build backend, run tests, restart the real systemd service, and smoke the live API.

## Pitfalls

- **The update handler is the most commonly forgotten layer.** A partial fix often adds junction-table writes to `createTask` and junction-table reads to `getTask`/`listTasks`, but forgets to sync the junction table in `updateTask`. The update handler typically only processes `goalId` (singular, writes to `tasks.goal_id`) and ignores `goalIds[]` entirely — so even if the frontend sends multiple goals, editing a task silently drops all but the first. Always audit create, read, AND update handlers when restoring M:M.
- **Frontend types ≠ frontend behavior.** Having `goalIds?: string[]` in the DTO type and the API response does NOT mean the UI lets users pick multiple goals. The TaskDialog/creation form often only has a single `goalId` picker. When adding the UI, you must also extend the API-client type overloads for all paths (create, createForDate, update) — otherwise TypeScript will block the build. Check the actual form component AND the API-client type extensions, not just the DTO definitions.
- Do not treat the M:M fix as a frontend-only type change. The API read paths, write paths, and migration/backfill must all move together.
- Do not overwrite `tasks.goal_id` when linking a task to an additional goal; that recreates the original data-loss bug.
- If a manual background server is started while a systemd service already owns the port, the new binary may never serve requests. Verify `ss -tlnp` and restart the real service before trusting API smoke results.
- Keep rollback simple: because the old FK remains, old clients still have a primary goal while new clients can use `goalIds`.