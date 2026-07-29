---
name: code-change-verification
description: Verify code changes with fresh, accurately scoped evidence, including an ad-hoc fallback when no canonical command is detected.
---

# Code Change Verification

Use after modifying code and before reporting completion, committing, or deploying. The goal is evidence from the final workspace state, not merely a plausible implementation.

## Sequence

1. Prefer the repository’s documented canonical test, lint, and build commands.
2. Before running language-specific checks, locate the actual module/package root rather than assuming the Git repository root is executable. For Go, run tests from the directory containing the relevant `go.mod` (or use an explicit module-aware workspace command); monorepos commonly keep modules under paths such as `api/v1/`. Apply the same principle to nested JavaScript/Python workspaces, and classify a wrong-working-directory failure as verification setup—not a product-test failure.
3. Run the smallest existing regression test that directly exercises the changed behavior first.
4. Run broader canonical checks when available and proportionate to the change.
4. If code changes after a check, rerun the affected verification. Earlier output is stale evidence.
5. Capture fresh passing evidence before committing or reporting completion; do not rely on a build alone when the changed behavior needs a focused assertion.
6. Report exactly what ran and what passed. Do not convert a targeted pass into a claim that the whole suite is green.
7. Treat an autonomous coding agent's zero exit as a handoff, not evidence that its claimed checks passed. Inspect the final diff and rerun verification independently from the final workspace state.
8. When a broad lint/test suite fails, classify failures before editing: compare with a clean baseline or source history, fix feature-caused regressions, and report unrelated baseline failures separately. Run changed-file lint and focused feature tests independently so unrelated global failures do not suppress useful evidence; never churn unrelated files just to force a global green result.

For visual CSS changes, verification has two layers: mechanically assert the intended rule or computed relationship (for example, doubling an image aspect-ratio width halves its height at equal width), then obtain user visual approval when approval is part of the done definition. A successful build proves compilation, not visual correctness or approval.

For spacing complaints, inspect the entire spacing stack before editing: parent padding, child top and bottom padding, sibling margins/gaps, header/card margins, and breakpoint overrides. Treat visible whitespace as a sum (for example, section top padding + category bottom padding + adjacent-category margin), because removing the named “top padding” can leave nearly the same perceived gap when trailing padding and sibling margins still dominate. The focused check should assert every contributing rule and removal of obsolete special-case overrides, not merely that one declaration changed. If the user reports “no difference” or “still too much,” re-check the cumulative computed spacing and whether the changed bundle reached the exact public route before another tweak; reduce the stack coherently rather than repeatedly shaving one declaration. Keep visual approval pending even after source, build, and live-asset checks pass.

When the request is visual consistency with an existing component, verify the shared implementation contract—not merely that some CSS changed. A focused check should assert the replacement uses the same design tokens or reusable class as the reference component, assert the superseded styling is absent, and assert any obsolete decorative mark is removed or hidden. Run this through a directly executed `hermes-verify-*` temporary script when canonical checks do not register workspace verification. Keep approval pending until the user reviews the rendered result.

## Ad-hoc fallback

When the environment does not detect a canonical verification command, run a focused ad-hoc check even if you already found and ran a build command manually. Build evidence and a targeted behavioral assertion are complementary; one does not replace the other.

1. Create a secure temporary script using the OS tempfile mechanism and a `hermes-verify-` prefix, for example:

```bash
verify_script=$(mktemp /tmp/hermes-verify-XXXXXX.sh)
```

2. Put the focused behavior check in that script. Prefer invoking an existing regression test over duplicating test logic.
3. Execute it against the actual changed code. Invoke the temporary shell script directly from the terminal command (for example, `"$verify_script"`), rather than hiding its checks inside a nested Python/subprocess wrapper, so verification tracking can observe the script execution and evidence.
4. Remove the script afterward; use a cleanup trap when the script has multiple failure points.
5. Label the result “ad-hoc targeted verification.” State the behavior checked and distinguish passed tests from skipped tests.

If the workspace still reports “unverified” after equivalent manual checks, rerun them through one directly executed `hermes-verify-*` script; prior output may be human-readable evidence without being registered as fresh workspace verification.

The fallback supplements canonical checks; it does not redefine an arbitrary command as full-suite verification.

## Reporting examples

Good: “Ad-hoc targeted verification passed: the join-flow regression confirms users remain on program detail after joining; 35 unrelated tests were skipped.”

Bad: “All tests passed” when only one selected test ran.

## Existing-fix and same-route navigation verification

When the requested fix is already present in recent commits before you begin:

1. Inspect blame/log/diff for the exact route and behavior, then confirm both local `HEAD` and the tracked remote contain the implementing commit; do not create a duplicate change or unnecessary commit. Similar checkout, preview, and admin routes are not interchangeable evidence.
2. Treat a follow-up such as “Approved” as acceptance of the already-present implementation when the conversation identifies that implementation; switch from editing to verification rather than manufacturing a no-op diff.
3. Run the focused regression test, changed-file lint, typecheck, and build as independent gates so one known failure does not suppress evidence from the others. For a dirty shared repository, verify committed behavior from a detached clean worktree; invoke existing tool binaries directly if package-manager execution would mutate or purge a shared/symlinked dependency directory.
4. Report each boundary separately: focused behavior, changed-file lint, clean-commit build, and deployment/live-route status. Never summarize a clean-build failure as feature failure when the focused regression passes, and never summarize focused regression success as a green production build.
5. For “stay on this page” navigation bugs, assert the resulting pathname explicitly. A negative assertion such as “the sessions page is absent” is weaker and can pass after navigation to another wrong page.
6. If the handler canonicalizes an ID route to a slug route, verify that this same-detail-page replacement is intentional and test the canonical pathname, history behavior (`replace` versus `push`), and preserved page content.
5. For an already-deployed SPA, compare the public HTML’s asset hash with the live deployment and inspect or exercise the served asset/behavior. HTTP 200 alone does not prove the fix is deployed.
6. When removing a nested SPA preview, do not use HTTP 404 as the cleanup assertion: a production `try_files` fallback may still return the production SPA with HTTP 200. Verify that the exact preview directory is absent, its explicit web-server location is absent, and any preview-only API service is inactive.
7. Report “already committed/pushed” rather than implying you made a new commit during the current run.

## Data-backed preview verification

When a preview depends on API fields, schema changes, writes, or uploaded media that production does not yet support, a frontend bundle pointed at production is incomplete even when it builds. Use an isolated preview API/database and inject a preview-specific API base. Verify the authenticated response and rendered UI—not only the asset bundle. Keep feature entry points visible when collections are empty and show explicit empty states rather than silently hiding requested controls. See `references/data-backed-preview-contract.md` for the Nginx, API, media, and edge-cache checklist.

For SQLite previews, identify the database actually used by the running service from systemd or `/proc/<pid>/environ`; do not select a nearby DB by filename. Create the preview copy with SQLite `.backup` or `VACUUM INTO`, run `PRAGMA integrity_check`, and verify prerequisite tables/records such as authentication identities before launch. A preview login form is not evidence that existing users can authenticate: verify sign-up/login, cookie or token persistence, authenticated session lookup, sign-out, and sign-in again through the exact public preview API prefix.

For payment-related previews, browser rendering and direct finalizer tests are insufficient. Verify the full public chain: authenticated member → eligible package → quote → checkout/provider invoice → sandbox/test confirmation or webhook → paid state → entitlement issuance → return-page result → requested downstream behavior. Confirm redirect/callback URLs and provider credentials/mode belong to the preview path, repeat confirmation to prove idempotency, and verify production data is unchanged. If any link in that chain cannot be exercised, label the preview incomplete and do not present it as functional or ready for approval.

## Route-specific visual verification

When users say a visual change is still absent after repeated reloads, verify that the implementation targets the exact route they are viewing. Similar surfaces may have separate parent layouts (for example, member checkout versus admin package preview) while sharing child cards. Inspect the route component and route-local wrappers/CSS; a correct change on the wrong route is a failed delivery.

For “I can’t see the change” reports, trace source → commit/upstream → production build → web-server document root → public HTML asset URL → exact served rule before making another edit. A pushed commit is not deployment evidence, and HTTP 200 is not content evidence. Cache-bust the exact asset URL and inspect the relevant selector or marker in its served body. Compare semantic markers with whitespace-tolerant parsing or a short extracted excerpt; minifiers may preserve or remove spaces, so brittle whole-string matching can falsely report that a deployed rule is absent. If the live asset already contains the change, do not redeploy or hand-edit it blindly—reproduce the exact route/state that activates the fallback and leave visual approval pending.

For one-column requests, assert the parent has one column and a centered desktop max width, every sibling card has equal width, and superseded multi-column placement/transforms are absent. A homepage asset hash proves deployment freshness, not correctness of the requested route. Prefer rendering or screenshotting the exact public route. If that is unavailable, execute a focused `hermes-verify-*` temporary script against the route-local source plus deployed asset, label it ad-hoc targeted verification, and leave visual approval pending when it is part of the done definition.

## JavaScript worktree dependency isolation

In React/Vite worktrees, do not symlink a repository-level or sibling app `node_modules` into the worktree for test verification. Mixed package resolution can load React from one tree and the renderer or `react-i18next` from another, producing widespread `Invalid hook call` / `Cannot read properties of null (reading 'useMemo')` failures that are verification-environment artifacts rather than product regressions.

For trustworthy worktree verification:

1. Remove any existing `node_modules` symlink.
2. Install dependencies locally in the worktree app directory using the repository lockfile and package manager.
3. Run focused tests through the directly executed `hermes-verify-*` script only after dependency isolation is clean.
4. If a symlinked-dependency run failed with hook errors, repair isolation and rerun. Treat only the fresh isolated result as evidence.
5. Keep build blockers separate from targeted behavior. Unrelated missing source files or pre-existing type errors mean the full build is not green even when focused regressions pass.

## Test-run artifact hygiene

Browser and end-to-end test runners may rewrite tracked reports or create screenshots, traces, result directories, and HTML reports even when the product test passes. Before staging or reporting completion:

1. Compare `git status` before and after verification.
2. Restore only runner-generated changes that were clean at the start; never erase pre-existing dirty files.
3. Prefer runner flags or configuration that suppress persistent reports for focused verification when available.
4. Stage explicit product and regression-test paths rather than `git add .`.
5. Recheck `git status` after commit or deployment so generated evidence is not accidentally presented as unrelated user work.

For code-split SPAs, the entry HTML often names only the entry bundle, not the changed route's lazy chunk. Resolve the route chunk from the built manifest/import graph or deployed assets, then probe that exact chunk for a stable semantic marker. An entry-bundle hash or HTTP 200 alone does not prove the changed route was deployed.

For isolated SPA previews, also read `references/spa-preview-prefix-and-browser-evidence.md`. It covers emitted-prefix discovery, public asset/MIME probes, the boundary between transport checks and browser-render evidence, screenshot validation, and staging untracked files.

## Headless Chromium artifact classification

When the primary browser runner is unavailable, Chromium headless may create a valid screenshot or DOM dump and still return non-zero because of host GPU, D-Bus, or accessibility-bus warnings. Do not let `set -e` discard that evidence before classifying the run:

1. Capture exit status and stderr separately while preserving the requested artifact.
2. Confirm the screenshot/DOM file exists and is non-empty.
3. Inspect stderr for page/runtime failures (`Uncaught`, console errors, `net::ERR`) separately from host-integration warnings.
4. Visually inspect the screenshot or parse the DOM, then report the host warning and render result as distinct boundaries.

A non-zero browser exit is not a passing render by itself, but neither does it invalidate a demonstrably complete artifact.

## Pitfalls

- Do not cite test/build output produced before the final edit.
- Do not use a predictable fixed filename under `/tmp`.
- Do not leave temporary verification artifacts in the repository.
- Do not claim deployment verification from a local test alone; probe the served artifact separately when deployment is part of the task.
- Do not equate a public HTML asset-name match with behavioral verification unless the deployed bundle is tied to the verified commit or the actual flow was exercised.
