---
name: feature-social-provider-operations
description: Use when implementing social account OAuth, provider-limited hashtag research, binary media validation, or sanitized provider capability and account status surfaces.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, social, oauth, hashtags, media]
    related_skills: [feature-social-project-scheduling, feature-verified-social-inbox-capture]
---
# Feature: Social Provider Operations

## Account OAuth
Generate short-lived state bound to the initiating authenticated user; validate state/callback, exchange server-side, store tokens encrypted or protected, expose sanitized account DTOs, and support select/disconnect. Mutable APIs never become public merely because an admin-token variable is absent. Mock mode refuses production.

## Hashtag research
Normalize and validate hashtags. Persist rolling distinct hashtag searches per provider account; enforce provider quota before API calls. Cache top and recent media separately with policy TTLs and unique `(provider_hashtag_id, result_type)` conflict targets. Malformed cache is a miss.

## Binary media validation
Inspect signatures and bounded metadata for PNG/JPEG/WebP and MP4 rather than trusting names/MIME headers. Apply platform/purpose constraints and reject malformed/truncated boxes safely.

## Configuration
Provider app/client ID, secret, exact redirect URI, graph/API version, OAuth state secret, public/frontend origins, database path. Never expose tokens/secrets.

## Templates
- `templates/social-provider-schema.sql`
- `references/oauth-hashtag-media.md`

## Pitfalls
Mock mixed into production handlers; auth optional by configuration; inaccessible publish media URL; provider quota only in memory; same TTL for top/recent; two serving backend lineages confused.

## Verification
State/user binding, token redaction, callback replay, disconnect, production mock refusal, rolling distinct quota, TTL separation, malformed cache, signature fixtures and malformed media.

## Provenance
`insta-scheduler` OAuth/account flow and `brand-organizer` hashtag/media utilities. Outbound scheduling remains in `feature-social-project-scheduling`.
