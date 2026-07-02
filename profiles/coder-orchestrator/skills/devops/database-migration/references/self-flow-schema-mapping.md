# Self-Flow: Drizzle PostgreSQL ↔ Go SQLite Schema Mapping

This project has two database backends with the same logical schema but different ORM conventions.

## PostgreSQL (Drizzle — Neon)

```
users(id uuid PK, email text, created_at timestamptz, updated_at timestamptz)
auth_users_ref(id uuid PK)  -- FK parent for users
goals(id uuid PK gen_random_uuid(), user_id uuid FK→users, title, description, category,
      status "Goal status" enum(active,done), start_date date, end_date date, created_at, updated_at)
task_groups(id uuid PK gen_random_uuid(), title, goal_id FK→goals, user_id FK→users, order_index int, created_at, updated_at)
tasks(id uuid PK gen_random_uuid(), user_id FK→users, parent_id FK→tasks, title, description,
      order_index int, status "Task status" enum(todo,in progress,blocked,completed,not done,delegated,commitment),
      effort "Task effort" enum(low,med,high), priority "Task priority" enum(low,med,high),
      group_id FK→task_groups, isTemplate boolean DEFAULT false, templateId uuid, created_at, updated_at)
task_goals(id uuid PK gen_random_uuid(), task_id FK→tasks, goal_id FK→goals, created_at)
energy_readings(id uuid PK gen_random_uuid(), user_id FK→users, level int, note, timestamp timestamptz, created_at)
habits(id uuid PK gen_random_uuid(), user_id FK→users, title, description, is_active boolean DEFAULT true, created_at, updated_at)
habit_options(id uuid PK gen_random_uuid(), habit_id FK→habits, label, score int, order_index int DEFAULT 0, created_at)
habit_logs(id uuid PK gen_random_uuid(), user_id FK→users, habit_id FK→habits, option_id FK→habit_options,
           date date, note, created_at, UNIQUE(user_id, habit_id, date))
focus_plan(id uuid PK gen_random_uuid(), user_id FK→users, date date, created_at)
focus_item(id uuid PK gen_random_uuid(), focus_plan_id FK→focus_plan, focus, description, percentage int)
```

## SQLite (Go API)

Same tables minus `auth_users_ref`, `assign_history`, `system`, `system_users`.

Column naming: snake_case (no camelCase).

Key differences from PG:
- All IDs: `text` (string UUIDs), not `uuid` type
- `is_template` INTEGER (0/1), not boolean
- `template_id` TEXT, not `templateId` uuid
- `tasks.goal_id` TEXT FK→goals (direct column — SQLite has BOTH this AND the `task_goals` junction table; populate both during migration)
- `tasks.assignee_id` TEXT (not in PG tasks — PG uses `assign_history` table)
- Timestamps: TEXT (ISO strings), not timestamptz
- Status/effort/priority: TEXT with CHECK constraints, not custom PG enums
- `users` has `name` TEXT and `password_hash` TEXT columns (not in PG)
- No `gen_random_uuid()` default — IDs are generated in Go app code

## Migration: SQLite → PG (this session's approach)

1. Insert into `auth_users_ref` first (FK requirement)
2. `users`: map id, email, created_at, updated_at only (skip name, password_hash)
3. `goals`: status TEXT→"Goal status" enum (same values), dates TEXT→date
4. `tasks`: `is_template` int→bool, `template_id`→`templateId`, `goal_id`→task_goals junction. Use `psycopg2.extensions.quote_ident()` for camelCase columns.
5. `habits`: `is_active` int→bool
6. All other tables: direct column mapping with TEXT→uuid/TEXT→timestamptz auto-cast
