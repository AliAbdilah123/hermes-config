---
name: feature-approval-gated-ai-jobs
description: Use when implementing durable approval-gated AI coding jobs with queue lanes, provider session continuity, review feedback, restart reconciliation, isolated worktrees, and fork/merge conversations.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, ai, jobs, scheduler, approval, worktrees]
    related_skills: [paragentix-hermes-ai-feature, queue-scheduler-state-transitions]
---
# Feature: Approval-gated AI Jobs

## Contract
Persist job, run, event, attachment, conversation, and merge state before provider work. A lane owns one active run. Runtime paths are revalidated immediately before mutation. Provider `session_id` is persisted and reused for feedback/implementation. Completion enters review; only explicit approval advances delivery.

## State flow
`todo -> queued -> running -> review -> approved|todo|blocked|failed`. Feedback resumes the intended session. Startup reconciles interrupted provider sessions rather than assuming failure. SQLite busy errors get bounded retry.

## Configuration
`ADDR`, `WORKSPACE_ROOT`, `WORKTREE_ROOT`, provider base URL/model/token (write-only persisted settings), optional notification variables. Workspace/worktree roots must be absolute; resolved paths must remain beneath them.

## Required implementation
1. Conditional SQL claim enforces lane capacity.
2. Append-only job events accompany transitions.
3. Provider response stores session identity before exposing completion.
4. Review feedback and approval check current run/version.
5. Fork creation is compensating: DB/worktree failures clean both sides.
6. Merge preview stores a source watermark; confirmation rejects stale previews.
7. Startup reconciliation revisits running/session-missing jobs.

## Templates
- `templates/schema.sql`
- `templates/state-machine.md`
- `templates/path-confinement.go`
- `references/implementation-checklist.md`

## Pitfalls
Lane-head races; resumed feedback in a new session; trusting persisted paths; orphan worktrees; stale merge previews; terminal runs consuming queue slots; unbounded SQLite retry.

## Verification
Test concurrent claim, restart reconciliation, same-session feedback, path escape rejection, fork rollback, stale-watermark rejection, and exact transition/event pairs.

## Provenance
Paragentix scheduler/conversation/worktree implementation and tests.
