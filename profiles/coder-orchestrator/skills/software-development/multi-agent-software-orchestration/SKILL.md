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

## PRD Drafting Pitfalls

- Do not over-lock implementation assumptions in the first PRD when the user has only described the product goal. If a channel/provider choice materially affects architecture, ask or make it easy to revise.
- For omnichannel chat/inbox products, “from scratch” usually means do not clone/depend on broken existing platforms; it does not automatically mean “official APIs only.” Clarify whether WhatsApp should use official Cloud API or Baileys/QR-session integration before making the API choice non-negotiable.
- When the user corrects an integration choice, revise the published PRD/API contract immediately and keep the original stack stable unless the user explicitly approves a broader stack change.
- See `references/omnichannel-chat-integrations.md` for Baileys-oriented WhatsApp MVP notes and API contract patterns.

## PRD/API Artifact Publishing

When the orchestrator is asked to turn an idea into a PRD/API contract, create a visually readable HTML artifact and make it available at `<publicIP>/prds/<prd-title>-<uuid>.html` before asking for approval.

Minimum flow:
1. Draft concise PRD + API contract in one accessible HTML file: problem/goal, roles/personas, functional requirements, permission matrix, data model, API routes, key request/response examples, milestones, and open review questions.
2. If the user supplies a design reference image or asks for design-system-first delivery, include a dedicated design system section before implementation milestones: tokens, component inventory, layout patterns, visual QA expectations, and which product screens consume each component.
3. If the user's environment has an established house stack or deployment convention, make that the default even when the supplied product spec recommends a different stack. Do not present the spec's stack as the primary option unless the user explicitly asks to follow it. For this user's web apps, prefer the standard React + TypeScript (Vite), Go API, SQLite, nginx `/projects/<project>/` deployment pattern unless overridden.
3. Use a stable slug plus UUID in the filename to avoid collisions, e.g. `fnb-pos-system-<uuid>.html`.
4. Publish under the host's PRD web root (`/var/www/html/prds` when nginx uses a `/prds/` alias; otherwise configure an equivalent `/prds/` location), set world-readable permissions, reload/test nginx if config changed.
5. Verify the artifact with real HTTP output (at minimum local `200 OK`; public URL too when network path allows) before telling the user it is ready.
6. Ask for focused review decisions after the link, not a broad “thoughts?” — e.g. provider choices, data-ingestion approach, auth depth, single vs multi-tenant/outlet, deployment target, MVP scope switches.

Common review defaults for local-business/SaaS style projects when the user has not decided yet:
- Prefer import/seeded data first, but support a pluggable connector layer so scraping/API collection can be added or swapped safely.
- If generated customer websites are in scope, ask whether they deploy to this server/subdomains or to an external provider; do not assume Cloudflare Pages.
- If the market is Indonesia, plan i18n from the start and default the UI copy to Bahasa Indonesia unless the user says otherwise.

Pitfall: do not proceed directly to Kanban breakdown until the user has approved or refined the PRD/API contract.

## Local-autonomous execution after approval

If the user approves the PRD and explicitly says to continue without creating a repo/PR or waiting for further review, switch from the GitHub/PR path to a local autonomous path:

1. Keep the approved stack stable and work in the local project directory.
2. Create local git branches using the usual task naming pattern, e.g. `kanban/<task_id>-<slug>`, but do not create a remote repository, GitHub issues, or pull requests.
3. If mirroring the work into Hermes Kanban with per-task branches, use `--workspace worktree --branch <branch>`; `--branch` is rejected with `--workspace dir:<path>`. Initialize the repo and create an initial commit first so worktrees/branches have a base. In CLI JSON output, read the task id from `id` (not `task_id`).
4. Use implementer subagents for the concrete coding tasks and a final integration-review subagent, but do not insert manual user review gates unless the user asked for them.
5. Commit each completed task locally with a concise feature commit.
6. Finish with a deployed/runnable artifact and real verification output, not only a task summary.

This is especially important for this user's preferred workflow: autonomous Kanban-style coding progress with local branches/commits, no GitHub repo/PR creation unless explicitly requested, and testing/deployment at the end.

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