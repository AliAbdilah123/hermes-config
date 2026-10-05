---
name: feature-social-project-scheduling
description: Use when implementing project-scoped social posts with shared destinations, independent schedules, immutable publish snapshots, per-target results, restart-safe workers, media uploads, and asynchronous generation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, social-media, scheduling, publishing, media, jobs]
    related_skills: [queue-scheduler-state-transitions, meta-graph-api-integration]
---

# Feature: Social Project Scheduling

## Overview

A project groups reusable destinations and multiple posts. Each post remains independently editable and schedulable until publication. Scheduling freezes immutable versions and creates restart-safe publication runs with per-target outcomes; it does not queue mutable drafts directly.

## Configuration

Core: `ADDR`, `DATABASE_PATH`, `MEDIA_DIR`, `PUBLIC_BASE_URL`, `FRONTEND_BASE_URL`, `ALLOWED_ORIGIN`.

Provider credentials are server-only. Supported names found in the implementation include Meta/Instagram, Threads, OAuth, Google identity, media-generation, email, analytics, and export settings. Load `references/implementation-checklist.md` for the complete grouped inventory; expose only safe public IDs/redirect URLs through status/config endpoints.

## Core model

- `projects`: user-owned content containers.
- `posts`: independently editable/schedulable children.
- `project_targets`: shared destination selection.
- `post_media`: ordered media attachments.
- `project_versions` + `project_version_media`: immutable content snapshots.
- `publication_runs`: queue state and lifecycle.
- `post_targets`: per-destination status/provider ID/error/idempotency/attempts.
- `publication_attempts`: immutable audit.
- `project_preflight_snapshots`: validated destination snapshot.
- `project_schedule_requests`: idempotency key, payload hash, stored response.
- `generation_jobs/items`: leased asynchronous generation.

Use DB checks, unique active-job indexes, ownership triggers, immutable-history triggers, and foreign keys.

## Scheduling contract

1. Client retains a key for an unchanged payload after uncertain failure; rotates only after confirmation or payload change.
2. API hashes canonical payload, rejects key reuse with a different hash, and replays the stored response for duplicates.
3. Validate ownership, unique draft IDs, bounded batch size, future RFC3339 timestamps, preflight, targets, and media.
4. Freeze immutable versions/runs in one transaction.
5. Worker runs at startup and periodically, claims bounded due runs, resumes unfinished targets, and writes an attempt for each provider call.
6. Aggregate target states into `PUBLISHED`, `PARTIAL_SUCCESS`, or `FAILED`; never flatten multi-provider publication to boolean.

## Media contract

- Align frontend limits with server multipart limits.
- Generate server filenames under user-scoped directories.
- Validate ownership before attachment.
- Validate MIME signature and platform/purpose requirements, not extension alone.
- Write to a temporary file and atomically rename; remove temporary files on failure.
- Serve only cleaned paths confined beneath `MEDIA_DIR`.

## Templates

- `templates/social_publication_schema.sql`
- `templates/provider.go`
- `references/implementation-checklist.md`

Handlers, workers, workspace UI, and tests are application seams: adapt the implementation contract in the reference and preserve the target project's established stack.

## Pitfalls found in real implementations

1. SQLite writes while a cursor remained open deadlocked a single-connection pool; read/close before writes.
2. Queueing mutable posts changed content at publish time; immutable versions fixed it.
3. Boolean success lost per-target partial failures.
4. Rotating idempotency keys after ambiguous failures duplicated schedules.
5. Save loops modified published posts; published records must be locked.
6. Destination changes incorrectly touched published posts or left cached schedule responses valid.
7. Provider account IDs and local connection IDs were conflated.
8. Generic MIME checks accepted platform-incompatible media.
9. Direct writes using original extensions lacked atomicity and signature validation.
10. Mock generation must refuse production; provider mode requires HTTPS and a key.

## Verification checklist

- [ ] Same key/same payload replays; same key/different payload conflicts.
- [ ] Scheduling freezes the exact text, media order, and target snapshot.
- [ ] Restart resumes only unfinished targets without duplicate publication.
- [ ] Mixed target results become partial success with target-specific errors.
- [ ] Published posts reject edits and destination synchronization.
- [ ] Upload path traversal, MIME mismatch, oversize files, and cross-user attachment are rejected.
- [ ] Worker starts immediately and repeats with bounded claims/retries.
- [ ] Migration tests prove ownership, FKs, legacy backfill, and immutability.

## Provenance

Extracted from SocialZen’s React workspace and Go/SQLite implementation, especially `ProjectWorkspace.tsx`, `internal/posts/projects.go`, route/media handlers, publication migrations, and publisher/provider tests.
