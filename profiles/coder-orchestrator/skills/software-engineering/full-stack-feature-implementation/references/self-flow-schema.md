# Self-Flow Relational Schema

The canonical DB schema for Self-Flow (Go + SQLite, port 8096, `/home/ubuntu/projects/self-flow/`).

## Tables

```
users (id TEXT PK, email TEXT, name TEXT, password_hash TEXT, created_at, updated_at)
sessions (id TEXT PK, token TEXT, user_id TEXT FK→users CASCADE, created_at)
  INDEX: sessions(token)

goals (id TEXT PK, user_id FK→users CASCADE, title, description, category CHECK(Main/Yearly/Quarterly/Monthly/Weekly/Daily), status CHECK(active/done), start_date, end_date, created_at, updated_at)
  INDEX: goals(user_id), goals(category)

tasks (id TEXT PK, user_id FK→users CASCADE, parent_id self-FK→tasks CASCADE, title, description, order_index, status CHECK(todo/in progress/blocked/completed/not done/delegated/commitment), effort CHECK(low/med/high), priority CHECK(low/med/high), group_id FK→task_groups SET NULL, is_template INT, template_id self-FK→tasks, goal_id FK→goals SET NULL, assignee_id, created_at, updated_at)
  INDEX: tasks(user_id), tasks(parent_id), tasks(group_id), tasks(goal_id)

task_groups (id TEXT PK, title, goal_id FK→goals CASCADE, user_id FK→users CASCADE, order_index, created_at, updated_at)
  INDEX: task_groups(goal_id), task_groups(user_id)

energy_readings (id TEXT PK, user_id FK→users CASCADE, level INT CHECK(1-10), note, timestamp, created_at)
  INDEX: energy_readings(user_id), energy_readings(timestamp)

habits (id TEXT PK, user_id FK→users CASCADE, title, description, is_active INT, created_at, updated_at)
  INDEX: habits(user_id)

habit_options (id TEXT PK, habit_id FK→habits CASCADE, label, score, order_index, created_at)
  INDEX: habit_options(habit_id)

habit_logs (id TEXT PK, user_id FK→users CASCADE, habit_id FK→habits CASCADE, option_id FK→habit_options CASCADE, date, note, created_at)
  UNIQUE: habit_logs(user_id, habit_id, date)
  INDEX: habit_logs(user_id, date), habit_logs(habit_id, date)

focus_plan (id TEXT PK, user_id FK→users CASCADE, date, created_at)
  INDEX: focus_plan(user_id), focus_plan(date)

focus_item (id TEXT PK, focus_plan_id FK→focus_plan CASCADE, focus, description, percentage)
  INDEX: focus_item(focus_plan_id)
```

## Source

Original Drizzle ORM schema (Neon Postgres) was in `packages/db/src/drizzle/schema.ts`, deleted in commit `ef1ceef`. Retrieved via `git show ef1ceef^:packages/db/src/drizzle/schema.ts`.

The Go port uses SQLite with CHECK constraints instead of Postgres enums. `PRAGMA foreign_keys=ON`.

## Go backend

- Single file: `packages/api/v1/main.go`
- Uses `modernc.org/sqlite`, `db.SetMaxOpenConns(1)`
- Demo user: `demo@self-flow.local` / `demo123456` (id: `11111111-1111-4111-8111-111111111111`)
- API on port 8096, systemd service `self-flow-api`
