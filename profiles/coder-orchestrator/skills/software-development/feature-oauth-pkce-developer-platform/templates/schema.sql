PRAGMA foreign_keys=ON;
CREATE TABLE developer_apps(id TEXT PRIMARY KEY,owner_id TEXT NOT NULL,name TEXT NOT NULL,client_secret_hash TEXT NOT NULL,redirect_uris_json TEXT NOT NULL,scopes_json TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE oauth_codes(code_hash TEXT PRIMARY KEY,app_id TEXT NOT NULL REFERENCES developer_apps(id),user_id TEXT NOT NULL,redirect_uri TEXT NOT NULL,scopes_json TEXT NOT NULL,pkce_challenge TEXT NOT NULL,expires_at TEXT NOT NULL,consumed_at TEXT);
CREATE TABLE oauth_tokens(token_hash TEXT PRIMARY KEY,app_id TEXT NOT NULL,user_id TEXT NOT NULL,scopes_json TEXT NOT NULL,expires_at TEXT,revoked_at TEXT,created_at TEXT NOT NULL);
CREATE TABLE webhook_events(id TEXT PRIMARY KEY,app_id TEXT NOT NULL,event_type TEXT NOT NULL,payload BLOB NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE webhook_deliveries(id TEXT PRIMARY KEY,event_id TEXT NOT NULL REFERENCES webhook_events(id),endpoint TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('pending','delivering','delivered','dead')),attempts INTEGER NOT NULL DEFAULT 0,next_attempt_at TEXT,last_status INTEGER,last_error TEXT,delivered_at TEXT);
