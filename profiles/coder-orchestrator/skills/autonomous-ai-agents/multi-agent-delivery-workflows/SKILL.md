---
name: multi-agent-delivery-workflows
description: "Design and assess Hermes multi-profile software delivery workflows: idea → PRD/API contract → task decomposition/story points → Kanban routing → implementation/review/merge/deploy."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, multi-agent, kanban, profiles, orchestration, software-delivery]
    related_skills: [hermes-agent, plan, github-pr-workflow, requesting-code-review]
---

# Multi-Agent Delivery Workflows

Use this skill when the user asks whether their coding profiles/agents can run a software-house style workflow, or asks to design an orchestration system where multiple Hermes profiles implement tasks in parallel based on task complexity/model strength.

## Target workflow class

The common desired pipeline is:

1. Capture an idea.
2. Have `coder-orchestrator` produce a full PRD, including API contract.
3. Decompose the PRD into the smallest useful implementation tasks.
4. Assign story/complexity points and dependencies.
5. Put the task graph on Hermes Kanban for visibility.
6. Route each task to an agent/profile based on complexity and configured model strength.
7. Implement each task on its own branch or worktree.
8. Review with a reviewer profile.
9. Send fixes to a strong coder profile.
10. Merge to main and deploy according to the project stack.
11. Verify the deployed public URL before final response.

## Assessment checklist

When asked whether the workflow already exists, actively verify these pieces before answering:

- Profiles exist: `hermes profile list` and `hermes profile show <name>`.
- Per-profile models are configured: check each profile's `config.yaml` or `hermes profile show` output.
- `coder-orchestrator` has `delegation` and/or `kanban` toolsets available.
- Kanban config exists and dispatcher is enabled (`kanban.dispatch_in_gateway`, auto-decompose settings, stale claim timeout).
- Worker profiles have the tools needed to edit code: `terminal`, `file`, and Kanban worker access.
- A reviewer profile exists (for example `coder-reviewer`) and has review-oriented prompts/skills.
- There is a routing policy from story points/risk tags to profiles.
- There is a branch/worktree naming convention per task.
- There is a review → fix → merge → deploy gate.
- There is a public verification requirement after deploy.

Avoid claiming “implemented” just because Hermes has Kanban or delegation. Distinguish clearly between:

- **Foundation exists**: profiles, Kanban, dispatcher, auto-decompose, delegation.
- **Workflow productized**: configured models, routing policy, review/fix loop, branch conventions, deploy verification.

## Recommended routing policy

Use story points as the default routing signal, with risk tags able to override upward:

| Complexity | Assignee | Typical model | Task examples |
| --- | --- | --- | --- |
| 1–2 SP | `coder-small` or default cheap profile | small/free model | copy edits, small tests, tiny UI changes, docs |
| 3–5 SP | `coder-medium` | medium model | normal feature slices, CRUD, UI pages, service functions |
| 8–13 SP | `coder-strong` | strongest model | architecture, migrations, auth, data consistency, cross-stack integrations |
| review | `coder-reviewer` | strongest or review-tuned model | security, correctness, tests, maintainability |
| fixes after review | `coder-strong` | strongest model | repair failed reviews, reconcile conflicts, stabilize tests |
| merge/deploy | `coder-orchestrator` | strongest orchestration model | final validation, merge, deploy, public URL check |

Risk tags that should upgrade a task to `coder-strong`: auth/security, database migration, payment/billing, permissions, data loss, deployment changes, API contract design, cross-service integration, and flaky test/debugging work.

## PRD and task decomposition rules

The orchestrator's PRD should include:

- Goals and non-goals.
- Personas and core user journeys.
- UX/page requirements.
- Data model.
- API contract: endpoints, methods, auth, request/response schemas, validation, errors.
- Acceptance criteria.
- Edge cases and failure modes.
- Rollout/deploy plan.
- Observability and test plan.

Decomposed tasks should be:

- Atomic enough for one branch/worktree.
- Independently testable.
- Scoped to files/modules where possible.
- Explicit about acceptance criteria.
- Annotated with story points and risk tags.
- Linked with dependencies in Kanban rather than relying on prose ordering.

## Kanban graph shape

A practical board flow is:

`triage → specified → todo → ready → in_progress → review → changes_requested → merge_ready → deployed/done`

For each implementation task, create or link:

- parent PRD/spec task;
- implementation child task;
- review child task depending on implementation;
- fix task only if review fails;
- merge/deploy task depending on all merge-ready tasks.

Use `hermes kanban runs`, `hermes kanban log`, `hermes kanban tail`, and `hermes kanban stats` to inspect progress and failures.

## Branch/worktree convention

Require workers to isolate work:

- Branch: `task/<kanban-id>-<short-slug>`.
- Worktree if multiple workers edit the same repo in parallel.
- Commit only the task scope.
- Include tests or verification output in the Kanban completion comment.

## Review gate

Review tasks should check:

- Requirements and acceptance criteria.
- API contract compatibility.
- Tests/build/lint.
- Security and permission boundaries.
- Data migration safety.
- Code quality: DRY, readable, bounded file size, comments only where helpful.

If failed, the reviewer should mark changes requested and create/route a fix task to `coder-strong`, including concrete reviewer notes. If passed, mark merge-ready rather than immediately merging from a worker.

## User-facing artifact pattern

For users who prefer plan/PRD review artifacts, produce a styled HTML review document before implementation. Include:

- current-state assessment;
- gap analysis;
- target architecture;
- profile/model routing table;
- implementation plan;
- acceptance criteria;
- verified public link if published.

For this user's environment, documents intended for review should generally be stored under the relevant project path at `docs/<name>` and published under `/prd/<name>` when possible, then verified via the public URL.

## Pitfalls

- Do not confuse `delegate_task` with durable profile workers. `delegate_task` is useful for quick synchronous subtasks; Hermes Kanban is the right primitive for durable multi-profile implementation pipelines.
- Do not say a profile is configured just because it exists. Check for model/provider config.
- Do not route all workers through the orchestrator's model. The point is per-profile model economics and capabilities.
- Do not let workers merge directly to main. Keep merge/deploy as an orchestrator gate after review.
- Do not skip public deploy verification when the user expects a working product link.

## References

- `references/capt4ce-coding-profiles-kanban-workflow.md` — concrete assessment and plan pattern from a session about routing coder-small/medium/strong/reviewer profiles through Hermes Kanban.
