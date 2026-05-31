---
name: multi-agent-software-orchestration
description: "AI software house workflow: idea → PRD/contract → story breakdown → billable kanban → model-tiered agent execution with per-task branching, PR review, and orchestrator merge."
version: 0.1.0
metadata:
  hermes:
    tags: [multi-agent, orchestration, kanban, github]
---

# Multi-Agent Software Orchestration

> **Repo mapping note:** this workflow expects a `.ops/` directory inside the target repository. Since `.ops/` is repo-local and skills are global under `~/.hermes/skills/`, maintain a sync path from the global skill references/templates/scripts into each repo’s `.ops/`. One reliable pattern: copy from the global skill into `.ops/` before running the orchestrator, and re-sync any global script/template updates back to the repo.

Goal: replicate “software house” cadence
- Operator submits idea/work-request
- Agent produces full PRD + API contract
- Agent breaks into tasks with story points
- Orchestrator maps complexity to model tiers
- Each task gets its own branch -> PR
- Strong-model reviewer reviews PR
- Observability via dashboard/kanban
- Operator only approves merge

## Skill-Based Model

Execute via `gh` as owner/reviewer:
.ops/personas/<role>.md — owner, planner, architect, backend, frontend, database, devops, qa, reviewer
.ops/workflow/<name>.md — `issue_to_prd` , `breakdown` , `branch_pr` , `review` , `merge`

Install:
```bash
cp -r Skills\\Multi\\ .ops/
```

Execute:
```bash
gh issue create \
  --title "Feature: OAuth login" \
  --body "$(cat <<'EOF'
Idea: Add OAuth login with Google and GitHub.
[CONTEXT]
EOF
)"
```

Orchestrator runs:
```bash
.ops/scripts/orchestrate.sh <ISSUE_NUMBER>
```

Config: `.ops/config.json` (enables/disables roles/workflows).

Will produce `scripts/` as shell + `references/` as markdown templates.

Trigger requirement:
- Repo root MUST contain `.ops/` directory with the skill structure
- `ORCHESTRATOR_MODE=agent` env for agent-run mode
- `ORCHESTRATOR_MODE=human` env for human-run mode