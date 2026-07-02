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

# PG connection (read password from pgpass file)
with open('/tmp/.pgpass_self') as f:
    host, port, db, user, pwd = f.read().strip().split(':')
pg = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd, sslmode='require')
pc = pg.cursor()

sq = sqlite3.connect(DB_PATH)
sq.row_factory = sqlite3.Row
sc = sq.cursor()
sc.execute('PRAGMA foreign_keys = OFF')

# ── Clear existing data ──
for t in ['focus_item','focus_plan','habit_logs','habit_options','habits','energy_readings',
          'tasks','task_groups','goals','sessions','users','_migration_done']:
    sc.execute(f'DELETE FROM {t}')

# ── Placeholder users (if PG users table is empty but content references IDs) ──
pc.execute('''
    SELECT DISTINCT user_id::text FROM goals
    UNION SELECT DISTINCT user_id::text FROM tasks
    UNION SELECT DISTINCT user_id::text FROM energy_readings
    UNION SELECT DISTINCT user_id::text FROM habits
    UNION SELECT DISTINCT user_id::text FROM habit_logs
    UNION SELECT DISTINCT user_id::text FROM focus_plan
''')
user_ids = [r[0] for r in pc.fetchall() if r[0]]
for uid in user_ids:
    sc.execute('''INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
                  VALUES (?, ?, ?, NULL, datetime('now'), datetime('now'))''',
               (uid, f'{uid}@imported.local', 'Imported User'))
print(f'users: {len(user_ids)}')

# ── Goals ──
pc.execute('SELECT id::text, user_id::text, title, description, category, status::text, start_date::text, end_date::text, created_at::text, updated_at::text FROM goals ORDER BY created_at NULLS FIRST')
for r in pc.fetchall():
    sc.execute('INSERT INTO goals (id,user_id,title,description,category,status,start_date,end_date,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)', r)

# ── Tasks (with junction table flattening) ──
# Map first goal per task from task_goals junction into tasks.goal_id
pc.execute('SELECT DISTINCT ON (task_id) task_id::text, goal_id::text FROM task_goals ORDER BY task_id, created_at NULLS FIRST')
task_goal = dict(pc.fetchall())

pc.execute('''SELECT id::text, user_id::text, parent_id::text, title, description, order_index,
                     status::text, effort::text, priority::text, group_id::text,
                     "isTemplate", "templateId"::text, assignee_id::text, created_at::text, updated_at::text
              FROM tasks ORDER BY created_at NULLS FIRST''')
for r in pc.fetchall():
    tid = r[0]
    sc.execute('''INSERT INTO tasks (id,user_id,parent_id,title,description,order_index,status,effort,priority,group_id,is_template,template_id,goal_id,assignee_id,created_at,updated_at)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
               (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9],
                1 if r[10] else 0, r[11], task_goal.get(tid), r[12], r[13], r[14]))

# ── Energy, Habits, Focus, etc. ──
# (Add per your schema — pattern is the same: cast uuids to ::text, booleans to int)

# ── Finalize ──
sc.execute('INSERT INTO _migration_done (id) VALUES (1)')
sq.commit()
sq.close()
pg.close()
print(f'Done. Backup: {BACKUP}')
