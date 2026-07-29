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
6. **Verify preview end-to-end.** A preview subdirectory alone is insufficient: add an explicit Nginx `location ^~ /previews/<slug>/` with `alias`, SPA `try_files` fallback to that preview's `index.html`, and the correct router basename/API base injection. Back up the config, run `nginx -t`, reload, and verify the exact preview root and a deep route return the preview HTML—not production fallback HTML. Confirm public hashed JS/CSS return their real MIME types. Then render the public URL in a real headless browser and inspect the rendered DOM/screenshot: required page content must be present, `Page not found` must be absent, and relevant browser console/runtime errors must be absent. HTTP 200, correct asset URLs, or a successful build alone do not count as a working preview. Verify requested behavior at applicable desktop/mobile breakpoints and confirm production still serves its original artifact/SHA-equivalent state.
7. **Request approval.** Give the user the preview URL and clearly say production is unchanged and approval is pending. Apply requested revisions only in the feature worktree and preview.
8. **Handle rejection immediately.** If the user says `not approved` or clearly rejects the preview, remove its public route/assets immediately, verify it is no longer served as a separate preview, and leave production unchanged. Retain or remove the feature branch/worktree only according to the user's intent; do not merge it.
9. **Rebase before integration.** Immediately before approved integration, run `git fetch --prune origin main` again. If `origin/main` advanced, require a clean feature worktree, rebase onto it, and rerun verification. Stop and report any conflicts instead of resolving them automatically.
10. **Integrate only after explicit approval.** Re-verify the feature, squash-merge into the production branch, push, build from the clean merged commit, deploy the production artifact, and verify the public site and API. Confirm local and remote production SHAs agree.
11. **Cleanup last and prove it.** Remove the preview route/assets only after production verification succeeds. Then inspect the feature and temporary integration/deploy worktrees with `git status --porcelain`; never discard uncommitted files. For each clean worktree, verify its HEAD is contained in the freshly fetched remote default branch with `git merge-base --is-ancestor <sha> origin/<default>` before running `git worktree remove <path>`. Delete the corresponding local branch only after the containment check, run `git worktree prune`, and finish by checking `git worktree list --porcelain`. Cleanup is not complete—and must not be reported complete—while an approved feature's obsolete preview, integration, or deploy worktree remains registered. Generated-only dirt such as `node_modules` may be force-removed only after explicitly confirming it is the sole change; preserve all source/config/database changes for review.

## Preview safety

- Use unique slugs so concurrent previews cannot overwrite one another.
- Never use `/var/www/html/projects/komuna/` as the preview destination; that is the production document root.
- Back up Nginx configuration before editing it and run `nginx -t` before reload.
- Preview cleanup must target only the exact preview directory and route.
- Do not expose `.env`, databases, repository roots, source maps containing secrets, uploads not intended for review, or directory indexes.
- A frontend preview that talks to the live API must be labeled accordingly and exercised without destructive writes.

## Functional-preview parity gate

A Komuna preview is not reviewable merely because its HTML, assets, homepage, or changed component renders. Before sharing any preview URL, identify every prerequisite flow needed to reach and exercise the requested feature (for example authentication → program membership → package selection → checkout → provider confirmation → notification bell) and verify that complete chain on the exact public preview URL.

### Required environment parity

1. **Determine the real default branch.** Inspect `origin/HEAD`; if the repository uses `master`, fetch and branch from `origin/master`. Do not hardcode `main` and stop after that predictable failure.
2. **Use a clean worktree.** If the shared checkout is dirty, preserve it and create an isolated worktree from the freshly fetched remote default branch. Dirty shared state is not a reason to abandon implementation.
3. **Build for the exact preview path.** Set Vite `base` to `/previews/<slug>/`; generated `index.html` must reference `/previews/<slug>/assets/...`. Root-relative `/assets/...` is a failed preview even when those URLs return production assets with HTTP 200.
4. **Use an isolated but faithful database.** For SQLite, create the preview DB with SQLite `.backup`/`VACUUM INTO` from the actual runtime database identified from systemd or `/proc/<pid>/environ`; never guess among nearby `sqlite.db` files and never use raw copying with live WAL files. Run `PRAGMA integrity_check` and verify required table/record counts (including `auth_users`) before starting the preview API. The copy is isolated after creation: all preview writes must stay in it.
5. **Preserve required runtime configuration.** Inspect the production service's effective environment and copy only the non-production-safe configuration necessary for feature parity into the isolated preview process. For provider-backed features, explicitly decide whether the preview uses a provider sandbox/test account or an intentional stub. Never claim checkout/payment verification when provider credentials, callback token, invoice mode, redirect URL, webhook route, or reconciliation configuration is absent.
6. **Keep callback and return URLs preview-aware.** Checkout success/failure return URLs and provider webhook/callback routing must land on the preview API/UI or a documented sandbox bridge—not silently target production or an unavailable route. Do not mutate production data to make the preview work.

### Mandatory public flow checks before sharing

- **Authentication:** Exercise public sign-up or a known preview-safe login, capture the session cookie/token, call the authenticated session endpoint, sign out, sign back in, and confirm the browser reaches the intended authenticated route. A rendered sign-in form is not auth verification.
- **API routing:** From the browser/network or an equivalent cookie-jar flow, confirm requests use `/previews/<slug>/api/v1/...` and return JSON—not SPA HTML, production API responses, or 502/404 fallbacks.
- **Feature prerequisites:** Establish the exact roles, memberships, programs, products, packages, and records required by the feature in the preview DB. Verify the UI can reach the feature without manual URL guessing.
- **Payments/checkout:** When the requested feature involves payment, complete quote → checkout/invoice creation → provider sandbox confirmation or documented test finalization → paid purchase → entitlement issuance → return-page state. Then verify duplicate confirmation is idempotent and the requested downstream effect (such as a notification) appears. Merely opening Checkout or testing the finalizer directly is insufficient.
- **Notifications:** Verify the bell fetches from the preview API under an authenticated browser session, shows the generated event, updates unread state, and navigates to a real preview route whose page renders. An `href` assertion alone is insufficient.
- **Browser proof:** Render the exact public feature route in a real browser at desktop and mobile widths, inspect DOM and console/runtime errors, and exercise the primary interaction. If the normal browser tool fails, use installed Chromium headless with `--dump-dom`/screenshot and captured stderr; do not downgrade to HTTP-only evidence.
- **Production isolation:** Record production asset identity before and after, confirm it is unchanged, and verify preview writes affect only the preview DB/API.

### Truthful reporting

Report each gate separately: transport, rendered route, auth, prerequisite data, checkout/provider confirmation, downstream notification, and production isolation. If any required gate is unavailable, call the preview incomplete and do not send it as ready for review. Never use “functional preview,” “end-to-end verified,” or “ready for approval” based only on tests, builds, HTTP 200, direct handler tests, or a rendered login page.

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
- [ ] Preview route/assets removed only after successful production verification
- [ ] Clean obsolete preview/integration/deploy worktrees proven contained in remote default branch, removed, and local branches deleted
- [ ] Dirty worktrees preserved for review; generated-only forced cleanup explicitly verified
- [ ] `git worktree prune` run and final `git worktree list --porcelain` confirms no approved-feature leftovers
