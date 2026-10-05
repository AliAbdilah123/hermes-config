---
name: feature-oauth-pkce-developer-platform
description: Use when implementing third-party developer applications with exact redirect validation, OAuth authorization-code PKCE, hashed tokens, signed outgoing webhooks, retries, dead-lettering, inspection, and replay.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, oauth, pkce, webhooks, developer-platform]
    related_skills: [web-application-security-assessment]
---
# Feature: OAuth PKCE Developer Platform

## Contract
Register apps with exact redirect URIs and scopes. Authorization codes are short-lived, one-use, transactionally consumed, and bound to client, redirect URI, user, scopes, and PKCE challenge. Persist only token hashes. Outgoing webhook events are durable and signed; delivery attempts retry with bounds, then dead-letter and permit audited replay.

## Configuration
`HTTP_ADDR`, `DATABASE_PATH`, `RELAY_SECRET_KEY`, storage/public origins as needed. Production must reject a missing encryption/signing secret; never silently use a deterministic development key.

## Required implementation
- App/client registration and secret rotation.
- Consent and exact redirect matching.
- `S256` PKCE verification.
- Hashed access/revocation tokens and scoped middleware.
- Durable webhook event/delivery rows.
- HMAC signature over timestamp plus raw body; receiver enforces skew and constant-time compare.
- Worker closes read cursors before writes/network calls, records every attempt, applies backoff, dead-letters, and supports authorized replay.

## Templates
- `templates/schema.sql`
- `templates/pkce.go`
- `templates/webhook-signature.go`
- `templates/delivery-worker.md`
- `references/implementation-checklist.md`

## Pitfalls
Prefix redirect matching; reusable authorization codes; plaintext tokens; signing parsed JSON instead of exact bytes; network calls inside DB transactions; infinite retries; replay without audit.

## Verification
Test wrong redirect/client/verifier, code replay, expiry, scope enforcement, token revocation, signature tampering/skew, retry/dead-letter transitions, and replay authorization.

## Provenance
Relay developer platform, OAuth, webhook queue, delivery inspector, and milestone tests.
