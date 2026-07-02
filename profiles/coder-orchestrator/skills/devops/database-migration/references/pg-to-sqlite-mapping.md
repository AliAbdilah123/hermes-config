# PostgreSQL (Drizzle) → SQLite (Go API) Migration

This session's actual migration script, copying Neon Postgres data into the self-flow project's SQLite database.

## Schema mapping required

The PG database uses Drizzle ORM (camelCase columns, UUIDs, junction tables, PG enums).
The SQLite database uses the Go API schema (snake_case, text IDs, direct FK columns, text check constraints).

Key mappings:
- `tasks."isTemplate"` → `tasks.is_template` (camelCase → snake_case, bool → int)
- `tasks."templateId"` → `tasks.template_id` (camelCase FK)
- `task_goals(task_id, goal_id)` junction → `tasks.goal_id` direct FK (using `DISTINCT ON` to pick first goal)
- PG enum types → cast as `::text`
- `uuid` → `::text` cast

## Placeholder users pattern

The PG `users` table was empty but content tables (goals, tasks, energy_readings, etc.) referenced user IDs.
Created placeholder users for every distinct `user_id` found across all content tables:

```sql
INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
VALUES (?, ?, ?, NULL, datetime('now'), datetime('now'))
```

## FK-safe insert order

1. users
2. goals
3. task_groups
4. tasks
5. energy_readings
6. habits
7. habit_options
8. habit_logs
9. focus_plan
10. focus_item

## Tables skipped

- `sessions`: PG has no sessions table, so this table stays empty in SQLite.
- `_migration_done`: Always insert `(1)` after migration completes.
- `task_goals`, `assign_history`, `system`, `system_users`, `auth_users_ref`: Drizzle-specific tables not present in Go SQLite schema.
