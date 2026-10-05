PRAGMA foreign_keys=ON;
CREATE TABLE social_identities(id TEXT PRIMARY KEY,user_id TEXT NOT NULL,provider TEXT NOT NULL,provider_identity_id TEXT NOT NULL,verified_at TEXT,UNIQUE(provider,provider_identity_id));
CREATE TABLE inbox_integrations(id TEXT PRIMARY KEY,user_id TEXT NOT NULL,provider TEXT NOT NULL,account_id TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(provider,account_id));
CREATE TABLE message_receipts(provider TEXT NOT NULL,message_id TEXT NOT NULL,integration_id TEXT NOT NULL REFERENCES inbox_integrations(id),received_at TEXT NOT NULL,record_id TEXT,PRIMARY KEY(provider,message_id));
CREATE TABLE verification_replies(id TEXT PRIMARY KEY,integration_id TEXT NOT NULL,code_hash TEXT NOT NULL UNIQUE,expires_at TEXT NOT NULL,claimed_at TEXT,result TEXT);
CREATE TABLE external_media_cache(provider TEXT NOT NULL,media_id TEXT NOT NULL,owner_id TEXT NOT NULL,original_url TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('missing','claiming','available','failed')),claimed_at TEXT,cached_path TEXT,content_type TEXT,error TEXT,updated_at TEXT NOT NULL,PRIMARY KEY(provider,media_id,owner_id));
