---
name: feature-otp-community-platform
description: Use when implementing an OTP-authenticated community platform with governed conversations, moderation and blocking, explainable matching, notification digests, and privacy-safe funnel analytics.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, otp, messaging, moderation, matching, notifications]
    related_skills: [feature-multi-tenant-saas]
---
# Feature: OTP Community Platform

## Authentication
Hash OTP and session tokens. Enforce expiry, one-use consumption, request limits, revocation, CSRF rotation, Secure/HttpOnly/SameSite cookies, and production config validation. Log sender is development-only; production uses SMTP/provider delivery.

## Collaboration and safety
Accepting a response creates the conversation and exactly two memberships atomically. Composite foreign keys prevent non-member senders. Blocks apply symmetrically across discovery, responses, conversations, and messages. Moderation validates target types/roles and commits state with audit.

## Discovery and communication
Matching uses deterministic bounded weights and returns reason contributions that sum to the score. Notifications use semantic dedupe keys. Digest selection closes rows before writes, sends outside transactions, and records outcome/retry.

## Privacy analytics
Only server-generated allowlisted events with empty or tightly bounded metadata. Dedupe retries by entity and expose aggregates, not raw user-event streams.

## Configuration
`APP_ENV`, `HOST`, `PORT`, `DATABASE_PATH`, `SERVER_SECRET`, `COOKIE_SECURE`, `ALLOWED_ORIGIN`, `APP_BASE_PATH`, `DIGEST_ENABLED`, SMTP variables and bounded timing/rate settings. Build/runtime base paths must match. Trusted-proxy behavior requires an explicit design, not blind forwarded headers.

## Templates
- `templates/otp-session-schema.sql`
- `templates/community-schema.sql`
- `references/matching-notify-funnel.md`
- `references/verification-cases.md`

## Pitfalls
Production OTP logging; spoofable forwarded IPs; service-only membership checks; one-surface blocking; SQLite rows open during digest writes; client analytics as a PII channel.

## Verification
OTP replay/expiry/rate/hash, persisted logout, atomic conversation membership, DB-level non-member rejection, two-way blocks, transactional moderation audit, score reasons, notification dedupe/retry, and no raw PII.

## Provenance
`temubisnis` canonical Go/SQLite and web implementation.
