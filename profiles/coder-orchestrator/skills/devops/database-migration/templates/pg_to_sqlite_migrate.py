#!/usr/bin/env python3
"""Template: Copy PostgreSQL (Drizzle ORM) data into SQLite (Go API schema).

Adapt for your project: update DB_PATH, pg connection, and schema mappings.
"""
import shutil, sqlite3
from pathlib import Path
import psycopg2

# ── Config ──
DB_PATH = Path('/path/to/sqlite.db')
BACKUP = DB_PATH.with_suffix('.db.bak-pg-copy')
shutil.copy2(DB_PATH, BACKUP)

# PG connection
pg = psycopg2.connect(
    host='<host>', dbname='<dbname>', user='<user>',
    password='<password>', sslmode='require'
)
pc = pg.cursor()

sq = sqlite3.connect(str(DB_PATH))
sc = sq.cursor()
sc.execute('PRAGMA foreign_keys = OFF')
sc.execute('PRAGMA journal_mode = WAL')

# ── Clear existing data (FK-safe order) ──
for t in ['focus_item','focus_plan','habit_logs','habit_options','habits',
          'task_goals','energy_readings','tasks','task_groups','goals',
          'sessions','users','_migration_done']:
    sc.execute(f'DELETE FROM {t}')

# ── Placeholder users (for FK references not in users table) ──
pc.execute("""SELECT DISTINCT user_id::text FROM goals
    UNION SELECT DISTINCT user_id::text FROM tasks
    UNION SELECT DISTINCT user_id::text FROM energy_readings
    UNION SELECT DISTINCT user_id::text FROM habits
    UNION SELECT DISTINCT user_id::text FROM habit_logs
    UNION SELECT DISTINCT user_id::text FROM focus_plan
    UNION SELECT DISTINCT user_id::text FROM task_groups""")
ref_user_ids = set(r[0] for r in pc.fetchall() if r[0])

pc.execute('SELECT id::text, email, created_at::text, updated_at::text FROM users')
pg_users = pc.fetchall()
for r in pg_users:
    ref_user_ids.discard(r[0])
    sc.execute("""INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
                  VALUES (?, ?, 'Imported User', NULL, ?, ?)""", r)
for uid in ref_user_ids:
    sc.execute("""INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
                  VALUES (?, ?, 'Imported User', NULL, datetime('now'), datetime('now'))""",
               (uid, f'{uid}@imported.local'))
print(f"users: {len(pg_users) + len(ref_user_ids)}")

# ── Goals ──
pc.execute("""SELECT id::text, user_id::text, title, description, category,
                     status::text, start_date::text, end_date::text,
                     created_at::text, updated_at::text
              FROM goals ORDER BY created_at NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO goals (id,user_id,title,description,category,status,
                                     start_date,end_date,created_at,updated_at)
                  VALUES (?,?,?,?,?,?,?,?,?,?)""", r)

# ── Task Groups ──
pc.execute("""SELECT id::text, title, goal_id::text, user_id::text,
                     order_index, created_at::text, updated_at::text
              FROM task_groups ORDER BY created_at NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO task_groups (id,title,goal_id,user_id,order_index,created_at,updated_at)
                  VALUES (?,?,?,?,?,?,?)""", r)

# ── Tasks (camelCase→snake_case, bool→int) ──
# Collect task_goals for both junction table AND direct tasks.goal_id column
pc.execute('SELECT task_id::text, goal_id::text FROM task_goals ORDER BY created_at NULLS FIRST')
tg_data = pc.fetchall()
task_goal_map = {}
for tg in tg_data:
    if tg[0] not in task_goal_map:
        task_goal_map[tg[0]] = tg[1]

pc.execute("""SELECT id::text, user_id::text, parent_id::text, title, description,
                     order_index, status::text, effort::text, priority::text,
                     group_id::text, "isTemplate", "templateId"::text,
                     assignee_id::text, created_at::text, updated_at::text
              FROM tasks ORDER BY created_at NULLS FIRST""")
for r in pc.fetchall():
    tid = r[0]
    sc.execute("""INSERT INTO tasks (id,user_id,parent_id,title,description,order_index,
                                     status,effort,priority,group_id,
                                     is_template,template_id,goal_id,assignee_id,
                                     created_at,updated_at)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
               (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9],
                1 if r[10] else 0, r[11], task_goal_map.get(tid), r[12], r[13], r[14]))

# ── Task Goals junction table (populate alongside direct column) ──
for tg in tg_data:
    sc.execute('INSERT OR IGNORE INTO task_goals (task_id, goal_id) VALUES (?,?)', tg)

# ── Energy Readings ──
pc.execute("""SELECT id::text, user_id::text, level, note, timestamp::text, created_at::text
              FROM energy_readings ORDER BY timestamp NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO energy_readings (id,user_id,level,note,timestamp,created_at)
                  VALUES (?,?,?,?,?,?)""", r)

# ── Habits (bool→int) ──
pc.execute("""SELECT id::text, user_id::text, title, description,
                     is_active, created_at::text, updated_at::text
              FROM habits ORDER BY created_at NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO habits (id,user_id,title,description,is_active,created_at,updated_at)
                  VALUES (?,?,?,?,?,?,?)""",
               (r[0], r[1], r[2], r[3], 1 if r[4] else 0, r[5], r[6]))

# ── Habit Options ──
pc.execute("""SELECT id::text, habit_id::text, label, score, order_index, created_at::text
              FROM habit_options ORDER BY created_at NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO habit_options (id,habit_id,label,score,order_index,created_at)
                  VALUES (?,?,?,?,?,?)""", r)

# ── Habit Logs ──
pc.execute("""SELECT id::text, user_id::text, habit_id::text, option_id::text,
                     date::text, note, created_at::text
              FROM habit_logs ORDER BY date NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO habit_logs (id,user_id,habit_id,option_id,date,note,created_at)
                  VALUES (?,?,?,?,?,?,?)""", r)

# ── Focus Plan ──
pc.execute("""SELECT id::text, user_id::text, date::text, created_at::text
              FROM focus_plan ORDER BY date NULLS FIRST""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO focus_plan (id,user_id,date,created_at)
                  VALUES (?,?,?,?)""", r)

# ── Focus Items ──
pc.execute("""SELECT id::text, focus_plan_id::text, focus, description, percentage
              FROM focus_item ORDER BY id""")
for r in pc.fetchall():
    sc.execute("""INSERT INTO focus_item (id,focus_plan_id,focus,description,percentage)
                  VALUES (?,?,?,?,?)""", r)

# ── Finalize ──
sc.execute("INSERT OR REPLACE INTO _migration_done (id) VALUES (1)")
sq.commit()
sq.close()
pg.close()

# ── Verify ──
vq = sqlite3.connect(str(DB_PATH))
vc = vq.cursor()
for t in ['users','goals','task_groups','tasks','task_goals','energy_readings',
          'habits','habit_options','habit_logs','focus_plan','focus_item']:
    vc.execute(f'SELECT COUNT(*) FROM {t}')
    print(f"  {t}: {vc.fetchone()[0]}")
vc.execute('PRAGMA integrity_check')
print(f"  integrity: {vc.fetchone()[0]}")
vq.close()
print(f"Done. Backup: {BACKUP}")
