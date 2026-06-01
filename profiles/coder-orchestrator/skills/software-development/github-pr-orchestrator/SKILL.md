---
name: github-pr-orchestrator
description: Kanban orchestrator + GitHub PR workflow for task-driven development with tiered worker/reviewer profiles, complexity routing, branch automation, and review gating.
version: 0.1.0
platforms: [linux, macOS, Windows]
metadata:
  hermes:
    tags: [github, kanban, orchestration, pr, multi-agent]
    related_skills: [kanban-orchestrator, github-pr-workflow]
---

# GitHub PR Orchestrator Workflow

Use this when running a kanban-driven coding pipeline where tasks are decomposed and dispatched to different worker profiles, then reviewed and merged.

## Prereqs
- `gh` is authenticated (`gh auth status`)
- A repo is cloned and the default branch is set
- Hermes has profiles: `orchestrator`, `worker-strong`, `worker-medium`, `worker-easy`, `reviewer`

## Complexity → profile mapping
- `high` -> `worker-strong`
- `medium` -> `worker-medium`
- `low` -> `worker-easy`
- `review` -> `reviewer`

## Task lifecycle
1. `orchestrator` decomposes an idea into kanban tasks with title, description, complexity, model, and assignee.
2. Worker dispatcher claims tasks and spawns workers.
3. Each worker:
   - `git checkout -b kanban/<task_id>-<slug>`
   - implements/scaffolds changes
   - opens a PR, unless the user explicitly selects local-branch-only mode
4. Reviewer is auto-assigned / linked to PR, or reviews local branch handoffs in local-branch-only mode.
5. `orchestrator` merges after approval, or coordinates local integration when PRs are skipped.

## Local-branch-only mode

Use this mode immediately when the user says to skip PRs, skip GitHub repo creation, avoid remote setup, or just work with branches.

Adjust every existing and future kanban task in the graph:
- Remove/override any instruction to create a GitHub repo or PR.
- Keep the branch rule: `kanban/<task_id>-<slug>`.
- Require a local commit on the task branch.
- Require verification output and handoff details in the kanban completion summary/comment instead of a PR body.
- If a worker blocked on `gh auth`, missing remote repo, or PR creation, comment the new rule, unblock the task, and dispatch again.
- For review tasks, review local branch diffs and kanban handoffs rather than GitHub PRs.

Pitfall: do not let loaded `github-pr-workflow` guidance override an explicit user request to skip PRs. User workflow preference wins; update task bodies and comments so workers do not repeatedly block on GitHub auth/remote state.

## Recommended scripts
Use shell scripts or a skill-backed playbook for PR creation to avoid brittle one-off commands.

## Pitfalls
- Don’t run workers on an unclean worktree.
- Preserve profile-level credentials; never hardcode keys in shared scripts.
