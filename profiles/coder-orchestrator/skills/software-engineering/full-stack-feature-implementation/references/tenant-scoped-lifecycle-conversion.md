# Tenant-scoped lifecycle conversion

Use this checklist when converting one domain record into another (for example, an assessment into an active sales record) in a multi-tenant product.

## Inspect first

- Find the canonical source and destination models, lifecycle states, initial destination state, role helpers, tenant middleware, activity system, migrations, and focused tests.
- Preserve domain boundaries: conversion links records; it does not clone the canonical parent or turn the source into the destination.
- Reuse the existing authorization and audit architecture rather than adding parallel systems.

## Conversion contract

1. Authenticate and derive tenant, membership, and role from server-side identity. Never trust client-supplied tenant or role.
2. Load the source and all referenced records tenant-scoped inside a transaction.
3. Validate source lifecycle eligibility and every destination invariant before insertion.
4. Require users to confirm meaningful mandatory fields; do not silently invent ownership, action, or deadline values.
5. Preserve source, parent, offer/product, contact (when supported), owner, and provenance links.
6. Use the approved existing initial destination stage.
7. Write the destination and audit/activity events in the same transaction.
8. Make retries idempotent: check for the existing destination and return it without duplicating audit events.

## Database guarantees

- Prefer a unique nullable source foreign key (or equivalent partial unique index) to make one-source-to-one-destination atomic under races.
- Enforce mandatory fields for active destination records at the database boundary where legacy compatibility permits it. A conditional trigger/check can preserve incomplete historical or inactive records while rejecting new incomplete active records.
- Test both clean bootstrap and upgrade behavior; do not delete legacy rows to satisfy a new invariant.

## Authorization matrix

- Keep collaborative workspace reads when that is the product rule; do not accidentally replace them with owner-only visibility.
- Separate normal assigned-record work from administrative operations such as imports, merges, member management, ownership changes, and privileged overrides.
- For every GET-by-ID and mutation: authenticate, derive tenant membership/role, scope the target query by tenant, apply any record-owner rule, and return 403/404 according to the product's non-leakage convention.
- Frontend `can_edit` and hidden controls are UX reflections only; direct API tests must prove the backend boundary.

## Minimum regression matrix

- Happy conversion preserves all relationships and creates one activity.
- Each mandatory destination field missing is rejected without partial rows.
- Ineligible source, unauthorized actor, and cross-tenant source/reference are rejected.
- A retry and a concurrent duplicate attempt return one destination and one audit event.
- Owner/Admin/Member allowed and denied operations are exercised through direct APIs.
- Existing direct/legacy destination records remain readable.

## Delivery discipline

Keep the implementation report compact even when the request is large: files/areas changed, schema effect, conversion behavior, permission behavior, exact fresh checks, commit, and push. Avoid dumping autonomous-agent transcripts or broad diffs into the user-facing response.