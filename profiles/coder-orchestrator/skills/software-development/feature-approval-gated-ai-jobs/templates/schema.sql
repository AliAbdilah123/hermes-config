PRAGMA foreign_keys=ON;
CREATE TABLE jobs(id TEXT PRIMARY KEY,lane_id TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('todo','queued','running','review','approved','blocked','failed')),prompt TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE job_runs(id TEXT PRIMARY KEY,job_id TEXT NOT NULL REFERENCES jobs(id),status TEXT NOT NULL,provider_session_id TEXT,started_at TEXT,finished_at TEXT,error TEXT);
CREATE UNIQUE INDEX one_active_run ON job_runs(job_id) WHERE status IN ('queued','running');
CREATE TABLE job_events(id TEXT PRIMARY KEY,job_id TEXT NOT NULL REFERENCES jobs(id),run_id TEXT REFERENCES job_runs(id),kind TEXT NOT NULL,payload_json TEXT NOT NULL DEFAULT '{}',created_at TEXT NOT NULL);
CREATE TABLE job_conversations(id TEXT PRIMARY KEY,job_id TEXT NOT NULL REFERENCES jobs(id),parent_id TEXT REFERENCES job_conversations(id),worktree_path TEXT NOT NULL,head_sha TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE conversation_merges(id TEXT PRIMARY KEY,conversation_id TEXT NOT NULL REFERENCES job_conversations(id),source_head_sha TEXT NOT NULL,preview_json TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,confirmed_at TEXT);
