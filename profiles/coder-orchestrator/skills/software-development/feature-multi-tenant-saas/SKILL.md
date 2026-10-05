---
name: feature-multi-tenant-saas
description: Use when implementing a SaaS with user sessions, tenant memberships, tenant-admin and platform-superadmin surfaces, scoped authorization, invitations, immutable migrations, notifications, and audit logs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, multi-tenant, auth, rbac, go, react, sqlite]
    related_skills: [web-application-security-assessment, test-driven-development]
---

# Feature: Multi-tenant SaaS

## Overview

Use explicit platform and tenant roles, but authorize every tenant resource by membership and resource ownership. A role visible in the UI is not authorization. Keep auth and tenant modules composable and migrations independently owned.

## Configuration

Names only; secrets remain server-side:

- `ADDR`
- `DATABASE_PATH`
- `PUBLIC_BASE_URL`
- `SEED_SUPER_ADMIN_EMAIL`
- `SEED_SUPER_ADMIN_PASSWORD`
- `SEED_SUPER_ADMIN_TENANT`
- Optional integrations: `RESEND_API_KEY`, `RESEND_FROM_EMAIL`

Seed variables are bootstrap-only. Production startup must not rewrite an existing administrator’s password or log credentials.

## Data model

- `users`: normalized unique email, password hash, constrained platform role.
- `sessions`: random token hash, user, expiry, revocation metadata.
- `tenants`: organization identity/settings.
- `tenant_memberships`: unique `(tenant_id,user_id)`, constrained tenant role.
- `invitations`: tenant, email, role, hashed token, expiry, consumed timestamp.
- `audit_logs`: actor, tenant scope, action, subject, metadata, timestamp.
- `notifications` and per-user read state.

Enable SQLite foreign keys explicitly. Choose cascade versus set-null deliberately.

## Authorization boundaries

- `requireAuth`: resolve token/cookie, hash lookup, expiry/revocation check.
- `canAccessTenant`: require membership; superadmin bypass still verifies tenant existence.
- `canAdminTenant`: tenant admin/owner or platform superadmin.
- Platform routes require `platform_role == super_admin` explicitly.
- Load tenant-owned records using both `tenant_id` and record ID; never authorize only from a URL tenant ID and then fetch globally.
- SQL sort/filter columns come from allowlists, never raw query interpolation.

## Frontend surfaces

- `SessionProvider` rehydrates through `/api/v1/me`, clears invalid session state, and owns logout.
- Member navigation is membership-aware.
- Tenant dashboard exposes settings, users/invites, billing, and tenant catalog only to tenant admins.
- Superadmin dashboard exposes tenant/platform-user overview only to platform superadmins.
- Hiding navigation is UX; every backend route independently enforces authorization.

## Templates

- `templates/001_auth.sql`
- `templates/002_multi_tenant.sql`
- `references/implementation-checklist.md`

Backend middleware, React session/plugin composition, and security tests are framework seams: adapt the proven source patterns described in the reference rather than copying project-specific glue unchanged.

## Pitfalls found in real implementations

1. Browser bearer tokens were stored in `localStorage`; prefer Secure, HttpOnly, SameSite cookies when possible.
2. Wildcard CORS and logged seed credentials were unsafe defaults.
3. Startup repeatedly reset seeded administrator credentials.
4. Demo config endpoints exposed bootstrap account metadata.
5. Raw invite tokens were returned by API instead of delivered through a controlled channel.
6. Foreign keys were declared without proving `PRAGMA foreign_keys=ON`.
7. Imperative “ensure column” mutation replaced versioned migrations.
8. Plugin sources lived behind an external symlink; extraction must vendor or document them.
9. UI tests drifted from plugin navigation behavior; do not claim coverage without fresh runs.

## Verification checklist

- [ ] Cross-tenant direct-ID access is denied for reads and writes.
- [ ] Members cannot call tenant-admin or platform-admin routes.
- [ ] Tenant admins cannot administer other tenants.
- [ ] Superadmin bypass still rejects nonexistent tenants.
- [ ] Registration/invite consumption is transactional and tokens are one-time.
- [ ] Session expiration/revocation and logout work server-side.
- [ ] Migration IDs/checksums are deterministic and checksum drift is rejected.
- [ ] Member, tenant-admin, and superadmin frontend shells match backend capabilities.
- [ ] Fresh database migration and backend/frontend tests pass.

## Provenance

Canonical structure: Boilerplate Core plus `auth-basic` and `multi-tenant` plugins. Behavioral/security regression evidence: `multitenant-auth-saas-boilerplate`. The monolithic reference frontend is not the structural template.
