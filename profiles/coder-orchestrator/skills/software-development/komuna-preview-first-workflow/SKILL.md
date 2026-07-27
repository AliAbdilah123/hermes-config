---
name: komuna-preview-first-workflow
description: Use whenever a user asks to create, implement, redesign, revise, or materially change the Komuna website. Enforces an isolated public-preview approval gate before production integration or deployment.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [komuna, preview, worktree, approval-gate, deployment]
    related_skills: [responsive-prototype-refinement, responsive-prototype-production-handoff, github-pr-workflow, nginx-server-admin]
---

# Komuna Preview-First Workflow

## Scope

Apply this workflow only to creation or implementation work for the Komuna website repository at `/home/ubuntu/projects/komuna`. It covers features, redesigns, new pages/components, and material visual or behavioral revisions.

Do not apply it to read-only questions, investigations, reports, production incident mitigation explicitly authorized by the user, or other projects.

## Non-negotiable approval gate

A working preview, passing tests, a pushed feature branch, or positive-sounding feedback does not authorize production changes. Only an explicit user statement approving the preview authorizes integration and production deployment. If approval is ambiguous, production remains unchanged.

Before explicit approval, do not merge into `main`/`master`, push the production branch, replace production assets, restart production for the feature, or modify the production database.

## Workflow

1. **Synchronize the Komuna baseline.** This rule applies only to `/home/ubuntu/projects/komuna`. Before inspecting, planning, editing, building, or delegating implementation work, run `git fetch --prune origin main` from the shared Komuna repository and record `origin/main`'s SHA. Never use `git pull` for this preflight. Require the intended checkout/worktree to be clean with `git status --porcelain`; if it is dirty, preserve the changes and stop rather than stashing, resetting, or overwriting them automatically.
2. **Isolate from the newest main.** Create each new feature branch and separate worktree directly from the freshly fetched `origin/main`; never implement preview work in the production checkout. For an existing clean feature worktree, run `git rebase origin/main` before continuing. If the rebase conflicts, stop with the rebase paused and report the conflicting files; never guess at conflict resolution or modify another active worktree.
3. **Inspect safely.** Inspect the repository, production branch, remote, deployment layout, and current public production URL. Preserve unrelated work and confirm the recorded baseline SHA still identifies the fetched `origin/main`.
4. **Implement and verify.** Make only task-related changes in the worktree. Run focused tests, changed-file checks, and the production build. Build from the feature commit or a clean feature worktree; never publish an artifact containing unrelated dirty changes.
5. **Publish a separate preview.** Deploy to a unique non-production directory and URL, normally `/var/www/html/projects/komuna/previews/<slug>/` and `https://komuna.ahsanworks.com/previews/<slug>/`, or another isolated verified route when subpath constraints require it. Route preview API calls deliberately; never mutate production data merely to demonstrate UI.
6. **Verify preview.** Confirm the exact preview route and assets return successfully, the SPA deep route works, browser console has no relevant errors, and the requested behavior works at applicable desktop/mobile breakpoints. Verify production still serves its original artifact/SHA-equivalent state.
7. **Request approval.** Give the user the preview URL and clearly say production is unchanged and approval is pending. Apply requested revisions only in the feature worktree and preview.
8. **Handle rejection immediately.** If the user says `not approved` or clearly rejects the preview, remove its public route/assets immediately, verify it is no longer served as a separate preview, and leave production unchanged. Retain or remove the feature branch/worktree only according to the user's intent; do not merge it.
9. **Rebase before integration.** Immediately before approved integration, run `git fetch --prune origin main` again. If `origin/main` advanced, require a clean feature worktree, rebase onto it, and rerun verification. Stop and report any conflicts instead of resolving them automatically.
10. **Integrate only after explicit approval.** Re-verify the feature, squash-merge into the production branch, push, build from the clean merged commit, deploy the production artifact, and verify the public site and API. Confirm local and remote production SHAs agree.
11. **Cleanup last.** Remove the preview route/assets only after production verification succeeds. Then remove/prune the feature worktree and branch when safe.

## Preview safety

- Use unique slugs so concurrent previews cannot overwrite one another.
- Never use `/var/www/html/projects/komuna/` as the preview destination; that is the production document root.
- Back up Nginx configuration before editing it and run `nginx -t` before reload.
- Preview cleanup must target only the exact preview directory and route.
- Do not expose `.env`, databases, repository roots, source maps containing secrets, uploads not intended for review, or directory indexes.
- A frontend preview that talks to the live API must be labeled accordingly and exercised without destructive writes.

## Approval interpretation

Explicit approval examples: `approved`, `I approve this preview`, `merge and deploy this`, or an equally direct instruction referring to the reviewed preview.

Not approval: `looks interesting`, `preview works`, `thanks`, silence, a request for another revision, or merely asking whether it can be deployed.

## Verification checklist

- [ ] `origin/main` freshly fetched and its SHA recorded before Komuna implementation
- [ ] Intended checkout clean; unrelated dirty work preserved without automatic stash/reset
- [ ] Feature branch and isolated worktree created from fetched `origin/main`, or existing branch rebased cleanly
- [ ] `origin/main` fetched again and feature rebased if needed immediately before integration
- [ ] Production checkout and production assets unchanged before approval
- [ ] Feature tests/checks and clean build completed
- [ ] Separate preview URL published and browser-verified
- [ ] Exact preview URL supplied with approval explicitly requested
- [ ] Revisions applied only to preview before approval
- [ ] Rejected preview removed immediately
- [ ] Explicit approval captured before merge/push/deploy
- [ ] Squash merge, remote SHA, clean production build, and live production verified
- [ ] Preview removed only after successful production verification
