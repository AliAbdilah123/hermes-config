PRAGMA foreign_keys = ON;
CREATE TABLE tenants (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE tenant_memberships (tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, role TEXT NOT NULL CHECK(role IN ('member','admin','owner')), PRIMARY KEY(tenant_id,user_id));
CREATE TABLE invitations (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE, email TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('member','admin')), token_hash TEXT NOT NULL UNIQUE, expires_at TEXT NOT NULL, consumed_at TEXT);
CREATE TABLE audit_logs (id TEXT PRIMARY KEY, tenant_id TEXT REFERENCES tenants(id) ON DELETE SET NULL, actor_user_id TEXT REFERENCES users(id) ON DELETE SET NULL, action TEXT NOT NULL, subject_type TEXT NOT NULL, subject_id TEXT, metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE INDEX audit_tenant_created_idx ON audit_logs(tenant_id,created_at DESC);
