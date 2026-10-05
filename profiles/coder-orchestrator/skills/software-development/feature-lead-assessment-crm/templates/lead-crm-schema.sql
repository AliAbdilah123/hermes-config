PRAGMA foreign_keys=ON;
CREATE TABLE businesses(id TEXT PRIMARY KEY,tenant_id TEXT NOT NULL,name TEXT NOT NULL,normalized_name TEXT NOT NULL,source TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE import_rows(id TEXT PRIMARY KEY,batch_id TEXT NOT NULL,row_no INTEGER NOT NULL,outcome TEXT NOT NULL,error TEXT,business_id TEXT REFERENCES businesses(id),raw_json TEXT NOT NULL);
CREATE TABLE offer_versions(id TEXT PRIMARY KEY,offer_id TEXT NOT NULL,version INTEGER NOT NULL,criteria_json TEXT NOT NULL,published_at TEXT NOT NULL,UNIQUE(offer_id,version));
CREATE TABLE assessments(id TEXT PRIMARY KEY,business_id TEXT NOT NULL REFERENCES businesses(id),offer_version_id TEXT NOT NULL REFERENCES offer_versions(id),result_json TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE prospects(id TEXT PRIMARY KEY,assessment_id TEXT NOT NULL UNIQUE REFERENCES assessments(id),status TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE opportunities(id TEXT PRIMARY KEY,prospect_id TEXT NOT NULL UNIQUE REFERENCES prospects(id),stage TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL);
CREATE TABLE opportunity_stage_history(id TEXT PRIMARY KEY,opportunity_id TEXT NOT NULL REFERENCES opportunities(id),from_stage TEXT,to_stage TEXT NOT NULL,actor_id TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE outreach_attempts(id TEXT PRIMARY KEY,opportunity_id TEXT NOT NULL REFERENCES opportunities(id),idempotency_key TEXT NOT NULL UNIQUE,status TEXT NOT NULL,provider_id TEXT,error TEXT,created_at TEXT NOT NULL);
