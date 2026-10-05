---
name: feature-lead-assessment-crm
description: Use when implementing an auditable lead pipeline from CSV import and deterministic enrichment through immutable offer assessment, prospect conversion, governed CRM stages, files, and outreach.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, leads, import, enrichment, crm]
    related_skills: [feature-multi-tenant-saas]
---
# Feature: Lead Assessment CRM

## Workflow
Import known CSV schemas through explicit header mapping, row normalization, deterministic duplicate policy, bounded batches, and per-row audit. Keep enrichment in a stable rule registry. Publish immutable offer versions and bind assessments to their exact version.

Convert a qualified prospect and create its CRM opportunity atomically with an idempotency key; reject direct opportunity creation when lineage is required. CRM transitions use an explicit matrix, required-field checklist, optimistic version, immutable stage history, and scoped notes/tags/files/actions.

Private uploads use generated names, path confinement, and filesystem/DB compensation. Outreach records attempts and reuses the same key after ambiguous worker failure.

## Configuration
`DB_PATH`, `SESSION_SECRET`, `PUBLIC_BASE_URL`, `CRM_FILES_ROOT`, import byte/batch/duplicate controls, worker URL/secret, webhook secret, CORS/cookie settings.

## Templates
- `templates/lead-crm-schema.sql`
- `references/import-transition-files-outreach.md`
- `references/verification-cases.md`

## Pitfalls
Mutable offer history; direct CRM creation; new retry keys; open SQLite cursors before writes; filesystem/metadata divergence; compatibility columns replacing migrations.

## Verification
Audited row outcomes, deterministic duplicates, immutable assessment provenance, atomic/idempotent conversion, stale-transition rejection, file compensation, and outreach retry.

## Provenance
`local-business-os-indonesia` canonical Go/SQLite implementation.
