# Local Go + SQLite multi-tenant registration pattern

Use this when adding tenant registration and team invitations to this user's local Go + SQLite + React/Vite apps that currently have first-party email/password auth or a seeded admin.

## Backend shape

1. Add durable tenant tables:
   - `tenants(id, name, name_needs_update, created_at, updated_at)`
   - `tenant_members(tenant_id, user_id, role, created_at, updated_at)`
   - `tenant_invitations(id, tenant_id, email, role, token_hash, invited_by, accepted_by, expires_at, accepted_at, created_at)`
2. Backfill existing seeded/admin data into tenant `1` and ensure every existing user has a `tenant_members` row.
3. Add `tenant_id` to tenant-owned tables and default/backfill existing rows to tenant `1`.
4. Auth middleware should derive tenant context from the session user and inject both `tenantID` and tenant role into request context. Do not let handlers infer tenant from request body/query params.
5. Registration should create user + tenant + owner membership in one DB transaction, then issue a normal session.
6. Invite acceptance should validate token hash, email, expiry, and unaccepted state; then create the user and membership in one transaction and mark the invite accepted.

## API expectations

Typical endpoints:

- `POST /api/v1/auth/register` → creates a new tenant with a generated default name and `name_needs_update=true`.
- `GET /api/v1/tenant` → returns current tenant and role.
- `PATCH /api/v1/tenant` → owner/admin renames tenant and clears `name_needs_update`.
- `GET /api/v1/tenant/members` → lists current tenant members.
- `GET /api/v1/tenant/invitations` → lists current tenant invitations.
- `POST /api/v1/tenant/invitations` → owner/admin creates an invitation and returns a copyable invite URL/token when SMTP is not configured.
- `POST /api/v1/auth/invitations/accept` → accepts invite and creates member account.

## Tenant scoping checklist

Scope all read/write paths that expose tenant-owned data. At minimum audit:

- businesses and imports
- contacts and business-contact joins
- leads and CRM comments/stages
- script/templates
- WhatsApp conversations/messages
- website drafts/generated sites
- market reports/dashboard summaries
- bulk operations and CSV imports

For every handler, ensure `WHERE tenant_id=?` on reads and `tenant_id` is written from authenticated context on inserts. For update/delete, include both record id and `tenant_id`.

## Tests to add first

- Registration creates tenant and returns a session + tenant payload.
- First tenant rename clears `name_needs_update`.
- Owner/admin can create invitation; member role is stored.
- Invite can be accepted by matching email/token and creates a tenant member.
- Separate tenant users cannot see each other's businesses or CRM data.
- Existing seeded admin still logs in and sees backfilled default tenant data.

## Deployment pitfall

SQLite schema migrations run at service startup. If the systemd service runs as `www-data` or another non-owner user, the database directory must be writable by that user, not only the `.db` file. If startup logs show `attempt to write a readonly database` during migration, fix directory ownership/permissions, restart, then verify `/healthz` before public smoke tests.

## Public smoke tests

After build/restart/deploy:

1. Curl public bundle and confirm it contains registration/team UI markers.
2. Public `POST /auth/register` with a unique email/username; assert `tenant.name_needs_update == true` and CSRF/session are returned.
3. Use the returned cookie + CSRF to `PATCH /tenant`; assert the new tenant name and `name_needs_update=false`.
4. Use the same cookie + CSRF to `POST /tenant/invitations`; assert an invite URL/token is returned.
5. Login seeded admin and assert it still has default tenant data.
