# Implementation checklist

## Backend

Register public login/registration routes, authenticated `/me`/logout, tenant resources, and separate platform-admin routes. Generate session and invitation tokens with `crypto/rand`; persist only SHA-256 hashes. Prefer Secure, HttpOnly, SameSite cookies. Normalize email once before uniqueness checks.

Every tenant query must prove membership and include tenant scope in the data lookup. Platform-superadmin bypass still loads the tenant. Registration, tenant/membership creation, invitation consumption, audit insertion, and session creation use transactions.

## Frontend

A single session provider owns rehydration and logout. Route/nav registration consumes capabilities from `/me`; member, tenant-admin, and superadmin views remain distinct. UI visibility never replaces backend checks.

## Migrations

Keep auth and tenant migrations independently versioned. Record plugin-qualified IDs, content checksums, and applied timestamps. Apply each migration transactionally in deterministic order and reject checksum drift.

## Production hardening

No wildcard CORS, logged bootstrap credentials, repeated password resets, raw invite tokens in normal API responses, or public seed metadata. Enable SQLite foreign keys. Add rate limits, session revocation/cleanup, controlled invite delivery, and key rotation policy.

## Security tests

Test member/admin/superadmin matrices, cross-tenant direct IDs, nonexistent tenants, invitation replay/expiry, session expiry/revocation, SQL sort allowlists, fresh migration, and frontend capability rendering.
