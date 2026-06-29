# Capt4ce coding profiles → Kanban workflow assessment

This reference captures a concrete pattern for evaluating a user's desired “software house owner” multi-agent workflow in Hermes.

## User's desired flow

1. Create an idea.
2. Send it to `coder-orchestrator` to create a complete PRD through API contract.
3. Ask the orchestrator to break it down into smallest tasks and assign complexity/story points.
4. Push the task graph to Kanban for monitoring.
5. Have the orchestrator delegate tasks to profiles based on complexity and each profile's configured model:
   - hard → `coder-strong` with GPT 5.5;
   - medium → `coder-medium` with GPT 5.4;
   - easy → `coder-small` with `step-3.7-flash:free`;
   - review → `coder-reviewer` with GPT 5.5;
   - fixes after review → `coder-strong`;
   - merge/deploy → orchestrator.
6. Each task uses its own branch, is reviewed, fixed, merged to main, deployed, and verified.

## Verified assessment pattern

In the session that produced this reference, these checks were useful:

- Load `hermes-agent` skill first for authoritative commands/features.
- Run `hermes profile list` to inventory profiles.
- Use `hermes profile show <profile>` to check whether a profile is real and has model/env/SOUL configuration.
- Inspect `coder-orchestrator` config for:
  - model provider/default;
  - `delegation.max_concurrent_children`;
  - `delegation.max_spawn_depth`;
  - `kanban.dispatch_in_gateway`;
  - `kanban.auto_decompose`;
  - dispatcher stale timeout and failure limit.
- Check enabled toolsets with `hermes tools list`; `delegation` alone is not the same as `kanban`.
- Use `hermes kanban --help` to verify available board verbs (`create`, `decompose`, `dispatch`, `runs`, `log`, `tail`, `stats`, etc.).

## Example conclusion wording

Use this wording shape when foundation exists but the full workflow is not productized:

> Belum fully implemented. Hermes already has the foundations: profiles, Kanban durable board, dispatcher, auto-decompose, worker logs/runs, and delegation. But the end-to-end workflow still needs profile model configuration, a story-point routing policy, a reviewer profile/lane, branch-per-task conventions, review/fix gates, merge/deploy gates, and public deploy verification.

## Example gap table

| Capability | Status | What to check |
| --- | --- | --- |
| Profiles exist | often partial | `hermes profile list` |
| Per-profile models | often missing | each profile `config.yaml` / `hermes profile show` |
| Kanban engine | often present | `hermes kanban --help`, config `kanban.*` |
| Orchestrator tool access | partial | `hermes tools list`, config toolsets |
| Reviewer profile | often missing | `coder-reviewer` profile and review prompts/skills |
| Story point routing | usually missing | documented policy in skill/config/board prompts |
| Branch/worktree convention | usually missing | worker instructions and dispatcher prompts |
| Merge/deploy verification | project-specific | CI/build/deploy command plus public URL check |

## HTML plan artifact sections

When the user expects a review artifact, include:

- hero summary with assessment status;
- “Current State yang Terverifikasi” cards;
- “Kesimpulan” distinguishing foundation vs full implementation;
- “Target Architecture” table with lane/profile/model/task range/responsibility;
- “Implementation Plan” step list;
- “Config Sketch” for profile/model/routing;
- “Acceptance Criteria”.

## Nginx publication quirk from the session

The public PRD route in that environment mapped `/prd/` to `/usr/share/nginx/html/prds/`, not `/var/www/html/prd/`. If a symlink returns 403 because the target path is inaccessible to nginx, copy the HTML into the aliased directory and `chmod 644`, then verify the public URL contains expected text. Treat this as a publication troubleshooting pattern, not as a universal path rule.
