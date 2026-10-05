---
name: feature-verified-social-inbox-capture
description: Use when capturing Instagram or Facebook inbox messages into user-owned records with signed webhooks, dedicated-account verification, idempotent receipts, privacy isolation, and lazy recovery of expiring external media.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, social-inbox, webhooks, instagram, facebook, media-cache]
    related_skills: [meta-graph-api-integration, social-inbox-application-planning]
---
# Feature: Verified Social Inbox Capture

## Contract
Fail closed until provider feasibility and account ownership are proven. Verify webhook signatures against raw bytes, deduplicate provider message IDs, map only verified social identities to owners, and create records transactionally. Store original provider media URL/ID only during webhook handling; fetch media lazily from an owner-scoped detail endpoint.

## Configuration
Server-only provider app IDs/secrets, webhook verification token, dedicated inbox/account IDs, owner mapping, graph version, database path, secure-cookie setting, and public callback origin. Consolidate aliases; config/status DTOs expose readiness and public IDs, never secrets.

## Flow
1. One-time verification code proves control of the dedicated social account.
2. Signed webhook validates timestamp/signature and parses bounded input.
3. Receipt uniqueness makes retries safe.
4. Identity ownership and privacy scope are checked before record creation.
5. Media resolver claims a lease, allowlists provider hosts, bounds response size/type, caches successful bytes, preserves usable original references on failure, and permits later retry.

## Templates
- `templates/schema.sql`
- `templates/webhook-flow.md`
- `templates/media-cache-state.md`
- `references/implementation-checklist.md`

## Pitfalls
Trusting sender claims; duplicate retries; expiring URLs fetched synchronously in webhook; unsafe host redirects/SSRF; stale media claims; failure erasing original references; legacy env aliases masking drift; duplicate migration numbers.

## Verification
Test bad signatures, duplicate delivery, cross-user isolation, one-time verification, malformed/oversized attachments, host allowlist and redirects, lease cooldown/retry, successful cache reuse, and unavailable enrichment omission.

## Provenance
Social Notes Instagram/Facebook capture, verification, receipt, media-cache, permalink-recovery, and isolation tests.
