---
name: social-inbox-application-planning
description: Plan applications that route messages from dedicated social-media inboxes into user-owned records without requiring personal-account OAuth.
version: 1.0.0
metadata:
  hermes:
    tags: [planning, social-media, webhooks, identity, product-design]
---

# Social Inbox Application Planning

Use this skill when planning an application where users register a social identity and messages sent to a dedicated platform account become notes, tasks, tickets, leads, or other user-owned records.

## Core identity model

Separate the human-facing identity from the routing identity:

- `platform`
- `username`
- `normalized_username`
- nullable stable `platform_user_id`
- lifecycle status such as `pending | active | disabled`

Route by `(platform, platform_user_id)` whenever the provider supplies a stable sender ID. Use normalized username only when a real provider/API test proves it is reliably available and compatible.

Never describe a typed username confirmation as ownership verification. It is selection/registration unless the provider supplies proof.

## Required planning sequence

1. Define supported platforms and show only integrations that actually work.
2. Decide identity cardinality explicitly: one total, one per platform, or multiple per platform.
3. Put cardinality and ownership constraints in the database, not only the UI.
4. Keep the core product usable when social setup is skipped or provider access is delayed.
5. Run a provider feasibility spike before implementing message ingestion.
6. Lock the real webhook payload and identity-correlation contract using redacted fixtures.
7. Implement secure, idempotent ingestion only after the spike passes.
8. Validate authenticated public end-to-end flows, duplicate delivery, and cross-user isolation.

## Provider feasibility gate

Using the real dedicated/professional receiving account, prove current:

- account and business-asset requirements;
- permissions, app mode, and review requirements;
- webhook subscription and verification challenge;
- raw-body signature validation;
- sender identity fields and stable sender ID;
- external message/event ID;
- username/profile lookup capability;
- retry behavior and acknowledgement timing;
- ability to correlate a pending typed username with the first message.

Do not build ingestion from assumed or stale example payloads.

## Pending identity fallback

If arbitrary username lookup is unavailable:

`enter username → save pending → send first message → correlate sender → save stable ID → activate`

If the webhook exposes only an opaque sender ID and cannot resolve a compatible username, require a short-lived one-time code in the first message. This binds the sender without personal-account OAuth and avoids guessing.

The activating message may create the first record atomically. Older unmatched messages should not be retroactively imported unless the product explicitly requires it.

## Database invariants

For one identity per user per platform, enforce:

```sql
UNIQUE(user_id, platform)
UNIQUE(platform, normalized_username)
UNIQUE(platform, platform_user_id)
```

The stable ID may remain null while pending. Return generic “identity unavailable” conflicts without exposing the current owner.

Imported records should retain their source if an identity is removed. Prefer a nullable identity foreign key with `ON DELETE SET NULL` where historical records must survive.

## Webhook requirements

Plan for:

- bounded raw request bodies;
- verification token and signature checks;
- prompt acknowledgement;
- unique external message/event IDs;
- atomic event receipt, identity activation, and record creation;
- safe handling of malformed, unsupported, self-sent, duplicate, inactive, and unmatched events;
- no message-body logging by default;
- no retroactive import unless explicitly approved.

Do not add a queue until measured acknowledgement or retry behavior requires asynchronous processing.

## Dedicated inbox configuration boundaries

Keep the app-owned receiving account separate from user routing identities:

- Store the dedicated inbox in an app-level integration record (for example, `instagram_integration`), not in `social_identities`.
- The integration record owns the provider account ID, username, encrypted or prototype-null token, status, and timestamps.
- `social_identities` owns each app user's pending/active sender identity and stable provider sender ID.
- A real integration spans both sides: the provider app authorizes and subscribes the professional receiving account, while the backend records which account is authoritative.
- Keep app secrets and webhook verification tokens in environment configuration. Keep account identity and renewable credentials in the database unless explicitly designed otherwise.
- A webhook verification token is an application-generated random secret; a production account/user ID is provider-issued and must not be invented.
- A simulated prototype needs neither real scopes nor OAuth/webhook environment configuration. Seed an unmistakable prototype integration record and replace it in the real-provider phase.

## Verification-code prototype

A minimal safe prototype flow is:

`register username → pending identity → display short-lived one-time code → simulate DM → bind stable sender ID → active`

Requirements:

- Return and visibly display plaintext only when generating the code; persist a secure hash, expiry, and consumption state.
- Regeneration invalidates the previous code. Ten minutes is a reasonable default lifetime.
- Atomically match an unexpired, unused code and bind the incoming stable sender ID.
- Do not create a note from the verification message unless explicitly requested.
- After activation, route only by stable sender ID, never username.
- Deduplicate later messages by external message/event ID and test cross-user isolation.
- No admin approval is needed unless moderation is explicitly requested.

## Clarification and execution sequencing

When configuration questions precede implementation approval, answer them directly first and explicitly confirm that no changes were made. Separate real-integration requirements from simulated-prototype requirements so environment variables are not presented as prototype prerequisites. Once the user explicitly says to proceed, that is the implementation command; do not wait for another authorization. If asked whether work has started, state the current execution status first, then summarize scope briefly.

## Scope discipline

- Keep platform-specific handlers until a second integration exists.
- Do not create a generic provider/plugin framework for a one-platform MVP.
- A platform selector may contain one option; do not display future platforms as functional.
- Keep manual/core workflows available independently of social identity registration.
- Model replacement explicitly; a clean default is delete the current identity, then register the replacement anew.

## Plan deliverable

Include:

- confirmed product rules;
- feasibility gate;
- user flows and lifecycle states;
- data constraints and API conflicts;
- security/privacy requirements;
- ordered phases with gates;
- test and public E2E acceptance criteria;
- risks and fallbacks;
- an explicit implementation gate when approval is required.

For a worked decision checklist and acceptance matrix, see `references/identity-routing-checklist.md`.

## Subpath deployment and E2E traps

For a social-inbox SPA mounted below a path prefix:

- Build with the production base path and verify the deployed HTML points JS/CSS at that prefix. A root-base build may return HTTP 200 while failing to hydrate because assets are requested from `/_app/...` instead of the mounted path.
- After correcting the base, rerun the full authenticated workflow; asset transport checks are not feature evidence.
- Do not let a loose navigation regex match the project slug. For example, `/notes/` also matches `/projects/social-notes/login`. Match the exact route boundary via `URL.pathname`, then assert authenticated chrome or a protected API response before continuing.
- For two-user routing E2E, create unique users, visibly capture each code, activate distinct stable sender IDs, deliver and redeliver external message IDs, assert each user sees only their own note, then remove fixtures and require zero residual rows plus database integrity.

## Pitfalls

- Matching by username alone when stable IDs exist.
- Claiming username search before proving provider support.
- Allowing duplicate ownership because uniqueness exists only in frontend validation.
- Blocking the core app on optional social setup.
- Persisting unmatched message content “just in case.”
- Revealing which user owns an unavailable identity.
- Treating plan approval as implementation or deployment permission.
