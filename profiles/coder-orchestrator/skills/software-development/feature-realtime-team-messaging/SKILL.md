---
name: feature-realtime-team-messaging
description: Use when implementing workspace channels and direct messages with cursor history, threads, reactions, read state, drafts, SSE events, staged files, presence, notification preferences, and durable email outbox.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, messaging, realtime, sse, files]
    related_skills: [feature-multi-tenant-saas, feature-oauth-pkce-developer-platform]
---
# Feature: Realtime Team Messaging

## Model
Workspace-scoped channels/conversations contain membership, messages, edits/deletes, threads, reactions, read markers, drafts, saved items, files, and notifications. Every lookup includes workspace and membership scope.

## Realtime
SSE authenticates before subscribe and filters every event by recipient authorization. Reconnect uses event cursor; database remains source of truth. Presence is ephemeral and bounded, while read/unread state is durable.

## Files
Use staged upload -> MIME sniff/size validation -> generated confined path -> finalize attachment. Cleanup expires orphan stages. Downloads recheck membership; filenames never become filesystem paths.

## Notifications
Preferences, mute/DND, semantic dedupe, and email outbox are durable. Worker selects/closes rows, sends outside transactions, persists outcome/backoff, and avoids notifying active recipients when policy says so.

## Configuration
HTTP address, database path, storage root, application secret, public origin, mail provider settings and bounded upload/event limits.

## Templates
- `templates/messaging-schema.sql`
- `references/sse-files-notifications.md`

## Pitfalls
SSE broadcast without recipient checks; offset pagination drift; file trust from extension; orphan uploads; notification/network work inside transactions; DND applied only in UI.

## Verification
Cross-workspace denial, membership changes during SSE, cursor pagination, thread/reaction idempotency, read markers, file sniff/path/orphan cleanup, DND/mute, outbox retries.

## Provenance
Relay collaboration/messaging implementation and milestone tests; simple response-to-conversation messaging is also represented in `feature-otp-community-platform`.
