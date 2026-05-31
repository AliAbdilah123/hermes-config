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
   - opens a PR
4. Reviewer is auto-assigned / linked to PR.
5. `orchestrator` merges after approval.

## Recommended scripts
Use shell scripts or a skill-backed playbook for PR creation to avoid brittle one-off commands.

## Pitfalls
- Don’t run workers on an unclean worktree.
- Preserve profile-level credentials; never hardcode keys in shared scripts.
