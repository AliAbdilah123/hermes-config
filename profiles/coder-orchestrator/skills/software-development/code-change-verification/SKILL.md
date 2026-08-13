---
name: code-change-verification
description: Verify code changes with fresh, accurately scoped evidence, including an ad-hoc fallback when no canonical command is detected.
---

# Code Change Verification

Use after modifying code and before reporting completion, committing, or deploying. The goal is evidence from the final workspace state, not merely a plausible implementation.

## Sequence

### Hard completion gate

Before the first commit, push, or completion report, confirm the workspace has **registered fresh passing evidence**, not merely human-readable terminal output. When command detection is uncertain, proactively run a directly executed `/tmp/hermes-verify-*` script after the final edit; do not wait for an “unverified” warning and repair verification after pushing. Include a focused behavioral test plus the proportionate build/typecheck, remove the script, and label the result **ad-hoc targeted verification** rather than suite-green evidence.

1. Prefer the repository’s documented canonical test, lint, and build commands.
2. Before running language-specific checks, locate the actual module/package root rather than assuming the Git repository root is executable. For Go, run tests from the directory containing the relevant `go.mod` (or use an explicit module-aware workspace command); monorepos commonly keep modules under paths such as `api/v1/`. Apply the same principle to nested JavaScript/Python workspaces, and classify a wrong-working-directory failure as verification setup—not a product-test failure.
3. Run the smallest existing regression test that directly exercises the changed behavior first.
4. Run broader canonical checks when available and proportionate to the change.
4. If code changes after a check, rerun the affected verification. Earlier output is stale evidence.
5. Capture fresh passing evidence before committing or reporting completion; do not rely on a build alone when the changed behavior needs a focused assertion.
6. Report exactly what ran and what passed. Do not convert a targeted pass into a claim that the whole suite is green.
7. Treat an autonomous coding agent's zero exit as a handoff, not evidence that its claimed checks passed. Inspect the final diff and rerun verification independently from the final workspace state.
8. When a broad lint/test suite fails, classify failures before editing: reproduce each claimed baseline failure with the same command or smallest equivalent test in a clean worktree at the recorded upstream baseline. Source inspection or the fact that a changed feature seems unrelated is not proof that a failure is pre-existing. Fix feature-caused regressions and report only reproduced baseline failures separately. Run changed-file lint and focused feature tests independently so unrelated global failures do not suppress useful evidence; never churn unrelated files just to force a global green result.
9. For broad UI loading-state migrations, audit text mechanically across all relevant TSX/components, but verify by behavior class rather than file count: initial route loads, inline actions/buttons, pagination/search/upload, authenticated dashboard, privileged/admin routes, accessibility status labels, reduced-motion behavior, and layout-shift prevention. A build plus a zero-match text search is insufficient without representative focused tests and rendered public-route checks.

For visual CSS changes, verification has two layers: mechanically assert the intended rule or computed relationship (for example, doubling an image aspect-ratio width halves its height at equal width), then obtain user visual approval when approval is part of the done definition. A successful build proves compilation, not visual correctness or approval. When probing a minified deployed stylesheet, do not require source spelling: optimizers may serialize `transparent` as `0 0` in a background shorthand or otherwise normalize equivalent values. Prefer the browser's computed style on the exact rendered element; if using a stylesheet assertion, accept equivalent normalized forms and scope it to the complete selector rule so a match elsewhere cannot pass it.

For spacing complaints, inspect the entire spacing stack before editing: parent padding, child top and bottom padding, sibling margins/gaps, header/card margins, and breakpoint overrides. Treat visible whitespace as a sum (for example, section top padding + category bottom padding + adjacent-category margin), because removing the named “top padding” can leave nearly the same perceived gap when trailing padding and sibling margins still dominate. The focused check should assert every contributing rule and removal of obsolete special-case overrides, not merely that one declaration changed. If the user reports “no difference” or “still too much,” re-check the cumulative computed spacing and whether the changed bundle reached the exact public route before another tweak; reduce the stack coherently rather than repeatedly shaving one declaration. Keep visual approval pending even after source, build, and live-asset checks pass.

When the request is visual consistency with an existing component, verify the shared implementation contract—not merely that some CSS changed. A focused check should assert the replacement uses the same design tokens or reusable class as the reference component, assert the superseded styling is absent, and assert any obsolete decorative mark is removed or hidden. Run this through a directly executed `hermes-verify-*` temporary script when canonical checks do not register workspace verification. Keep approval pending until the user reviews the rendered result.

For a visual follow-up on an already-published preview, continue in that exact clean feature worktree and update the same isolated preview; do not create a second worktree for a revision to the same reviewed artifact. Conversely, a new request that merely touches the same domain is not continuation: create a fresh task worktree from the latest remote default branch instead of rebasing or reusing an older related preview. This distinction prevents stale feature history and avoidable conflicts from contaminating small changes.

## Database-backed private-file lifecycle verification

When a database row owns a private filesystem object, review failure ordering as a hard data-integrity gate. Neither “delete metadata, then remove bytes” nor “remove bytes, then delete metadata” is safe across partial failures. Use same-filesystem quarantine with restore-on-database-failure, and require forced-failure tests proving both metadata and original bytes survive. See `references/recoverable-private-file-deletion.md` for the sequence and regression matrix.

Do not let green happy-path upload/download/delete tests substitute for this review. Independently inspect error paths after implementation; file lifecycle defects commonly survive full test/build suites until a database trigger, permission error, or I/O failure is forced.

## Schema-migration and service-restart verification

Before deploying a newly authored migration, review the complete migration history as it will execute on both an existing database and a fresh database. If columns were added while the migration is still uncommitted and has never shipped, fold the final definitions into that migration's original `CREATE TABLE`; do not append an unconditional later `ALTER TABLE ADD COLUMN` for those same columns. A clean bootstrap would otherwise create the final schema and then fail while adding duplicate columns. Keep a follow-up migration only after the earlier migration has actually shipped, and test both upgrade and clean-bootstrap paths when practical.

After replacing a service binary and restarting it, `systemctl is-active` is only lifecycle evidence. The listener may not be ready yet. Poll the real local health endpoint with a bounded timeout, then probe the public route and expected content/API behavior. Treat an immediate connection refusal followed by healthy startup as a readiness race, not product failure; inspect status and journal if the bounded readiness check does not converge.

## Ad-hoc fallback

When the environment does not detect a canonical verification command, run a focused ad-hoc check even if you already found and ran a build command manually. Build evidence and a targeted behavioral assertion are complementary; one does not replace the other.

If verification tracking is required or likely to classify ordinary commands as unverified, make the directly executed `/tmp/hermes-verify-*` script part of the pre-commit gate. Run it before committing, pushing, deploying, or claiming completion—not as a repair after the completion report. A manually executed suite can be human-readable evidence while the workspace verifier still has no registered evidence; when command detection is uncertain, default to the tracked script before commit. The script should invoke the focused behavior test and any proportionate compile/build check from the real package root. In monorepos or nested frontends, `cd` inside the script to the directory containing the relevant `package.json`, `go.mod`, or equivalent; verification from the repository root can miss the canonical project context.

When selecting a focused test by name, inspect the runner summary and require at least one executed test. A zero-exit run where every test is skipped is not RED or GREEN evidence; broaden or correct the filter and rerun until the intended test actually executes. Do not let a later build or HTTP probe turn that zero-test script into “passed targeted verification.” Make the script fail explicitly when the runner reports only skipped tests (or parse the summary and assert executed > 0), then rerun with an exact current test name.

1. Create a secure temporary script using the OS tempfile mechanism and a `hermes-verify-` prefix, for example:

```bash
verify_script=$(mktemp /tmp/hermes-verify-XXXXXX.sh)
```

2. Put the focused behavior check in that script. Prefer invoking an existing regression test over duplicating test logic. For route changes, assert both the route helper and pathname parser, then run the focused test that exercises them.
3. Execute it against the actual changed code. Invoke the temporary shell script directly from the terminal command (for example, `"$verify_script"`), rather than hiding its checks inside a nested Python/subprocess wrapper, so verification tracking can observe the script execution and evidence. The script itself may call Python for source assertions, but the shell script must be the directly executed verification process.
4. Remove the script afterward; use a cleanup trap when the script has multiple failure points. Install the trap in the outer shell **before** executing the verifier. Do not rely on `status=$?; rm ...` after a verifier launched under outer `set -e`: a failed lint/test exits the shell before cleanup runs and leaves the temporary script behind. A safe shape is `verify_script=$(mktemp ...); trap 'rm -f "$verify_script"' EXIT; ...; "$verify_script"`. Report the exact temporary path and cleanup result so the evidence boundary is auditable.
5. Label the result “ad-hoc targeted verification.” State the behavior checked and distinguish passed tests from skipped tests.

If the workspace still reports “unverified” after equivalent manual checks, rerun them through one directly executed `hermes-verify-*` script; prior output may be human-readable evidence without being registered as fresh workspace verification.

The fallback supplements canonical checks; it does not redefine an arbitrary command as full-suite verification.

## Completion-state integrity

Keep task tracking and the final report aligned with the strongest evidence actually obtained:

- Never mark an E2E item completed when the browser flow timed out, authentication failed, fixture/onboarding setup returned an error, or only API/asset probes succeeded. Leave it pending, blocked, or cancelled with the exact boundary.
- Do not reinterpret a failed authenticated setup as successful E2E because deployment health, public assets, focused tests, or an unauthenticated route passed.
- If authenticated public E2E is required, do not use `READY`, “completed,” or an all-complete checklist until the exact public browser flow passes. Report `STOPPED` or “implemented/deployed; authenticated public E2E pending” when work is no longer actively executing.
- A final “unconfirmed” caveat does not repair an earlier completion claim or completed todo. Correct the status before reporting.

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

When the task is explicitly reviewable through a public preview, do not report “fixed” after only preflight, worktree creation, autonomous-agent launch, commit/push, focused tests, or a build. A dirty shared checkout is normally a reason to create an isolated worktree, not to stop. Continue autonomously through preview publication and exact public browser verification; avoid repeated progress-only final responses such as “preparing the preview.” The first completion report should include the public URL. If genuinely interrupted, use the precise state label “implemented; public E2E verification pending,” not “fixed,” and resume delivery without waiting for the user to ask where the preview is.

For uploaded images in an isolated preview, verify the full media contract: stored `/uploads/...` value → frontend preview-aware URL normalization → namespaced preview API media route → preview API upload directory. APIs that derive their uploads directory from the database location require media under the preview database's sibling `uploads/` directory, not merely under the worktree root. Probe a real public image and require its image MIME type. If a CDN previously cached a 404, retry with a cache-busting query and verify origin/public results separately. Also exercise the UI fallback for a broken image.

## Route-specific visual verification

### Separate route and modal surfaces

When a product has both a full detail route (for example `/items/:id`) and a board/list detail modal, treat them as separate delivery surfaces even when they share inner components.

1. Trace pathname parsing through the top-level route switch before changing a shared text renderer. A component-level render test can pass while the requested pathname still falls through to the board or another default view.
2. Inspect recent route commits and reverts. A reverted canonical-route change may explain why a shared modal works while the direct URL does not; do not blindly restore behavior that previously replaced the modal contract.
3. Preserve entry semantics explicitly: direct pathname navigation renders the full page, while clicking a list/card continues to open the modal without pushing a new pathname unless navigation was requested.
4. Add three focused regressions: pathname-to-route resolution, requested behavior rendered through the actual full-page wrapper, and unchanged modal/card navigation behavior.
5. For public verification, open the exact authenticated `/items/:id` route with representative persisted content. A shared component test, successful build, deployed bundle marker, or HTTP 200 is supporting evidence only and must not be reported as authenticated route E2E.

For authenticated settings/preferences previews, transport checks and a screenshot of the sign-in redirect are not feature evidence. Exercise authentication on the exact public preview, navigate to the intended settings tab through normal UI, change each preference, and verify persistence plus independence after reload. If authentication cannot be completed, report “public authenticated E2E pending” and do not call the preview ready for review.

When language and display currency are separated, verify both cross-combinations (English + canonical currency and Indonesian + converted display currency), confirm changing language leaves currency unchanged, and confirm display-only currency never alters quote, checkout, invoice, provider, or stored transaction currency. Also verify controls were removed from every superseded header/dashboard surface rather than duplicated.

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

## Mixed-version API/UI deployments

When a form is supposed to be prefilled from an API preview, do not stop at a leaf-component test that injects the desired prop directly. Test the real API-consumption/state-setting boundary with both current and legacy response shapes when frontend assets and a compiled backend can deploy independently. An empty-string fallback can silently turn contract drift into a blank field.

Trace and verify source commit → generated SPA bundle → compiled service binary → running process → public API shape → authenticated rendered control. Rebuild the exact executable named by systemd; a Git push or frontend build does not update a stale backend binary. During mixed-version windows, use a minimal compatibility normalizer that prefers the current field and deterministically converts the legacy field. Keep completion status pending until the exact authenticated public form is visibly non-empty and the operation succeeds.

See `references/mixed-version-api-ui-deployment.md` for the regression shape, dirty-checkout isolation, deployment chain, and truthful reporting boundary.

## Mutation refresh and request-budget verification

When optimizing frontend refetch behavior after task/goal or other nested CRUD mutations, define the mounted datasets and an explicit request budget per mutation before editing. Patch returned entities locally for ordinary mutations, refetch a scoped container query only when the mutation introduces unknown membership, and reserve hierarchy-cache refreshes for actual relationship changes. Browser verification must isolate initial-load and dialog-open requests from the post-mutation window; a GET observed nearby is not automatically mutation-triggered. Keep the result WORKING if any sibling flow still exceeds its budget, even when the primary regression passes. See `references/mutation-refresh-contract-verification.md` for the mutation matrix, race-detection test shape, and authenticated public request-count proof.

## Interactive job-operation verification

For UI operations that change backend state, do not stop at a component test or build. Add or update a focused test for the operation's availability in each required lifecycle state, then exercise the API boundary for the corresponding persisted transition. If an operation expands from one status to all statuses, update stale tests that assert the old restriction. For destination selectors that can create records, verify both existing-destination and new-destination paths, including optional generated names, validation, ordering, authorization, and preservation of active run/session identity.

When a move/reparent operation creates a destination inside a transaction, explicitly clear expected `sql.ErrNoRows`/not-found probe results before continuing; otherwise a successful lookup-for-absence can poison the later transaction and produce a misleading destination-validation error. Return the actual created destination ID, not a sentinel such as zero, and assert both the response ID and persisted foreign-key/lane change. In the UI, refresh the destination list when opening the dialog rather than trusting a stale board snapshot. If the user still reports failure after source tests pass, treat runtime freshness as a first-class boundary: identify the service's exact `ExecStart`, rebuild that binary and the served frontend artifact, restart, verify the public asset hash changed, then exercise the exact authenticated public payload and persisted board state. Do not create another speculative source patch until this boundary is checked. See `references/move-operation-verification.md` for the focused regression and deployment recipe.

## Queue/status UI differentiation verification

When changing UI copy or indicators that distinguish queued work from active provider processing, source tests and deployed-bundle string matches are supporting evidence only. They do not prove the exact public behavior.

1. Exercise an authenticated job detail through the public route in a genuinely queued state and assert the visible queued label plus its static/non-processing visual semantics.
2. Then exercise the same class of job after the scheduler claims it and assert the active provider-processing label plus its live indicator.
3. Check neighboring review, blocked, and done states do not retain either live queue/processing indicator.
4. Tie each rendered state to the API/persisted lifecycle value so a mocked component render cannot mask a state-mapping defect.
5. If authenticated browser execution is unavailable, report “implemented and deployed; public authenticated E2E pending.” Do not promote public asset markers, HTTP 200, service-active status, unit tests, or build success into “completed” or “public E2E verified.”
6. Only include a final public link as completed evidence after the exact queued → processing flow was visibly exercised there.

## Queue-mediated retry and resume verification

When changing a retry/reply action from immediate execution to queued execution, verify both halves of the lifecycle rather than only the final result:

1. Immediately after the endpoint returns, assert the item is `todo`, positioned at the end of its sequential lane/queue, and carries the pending input needed for later resumption.
2. Assert no external agent/provider request occurred, no run was marked `running`, and attempt/run counts did not change during enqueueing.
3. Assert the timeline records a pending acknowledgement such as “Reply sent — pending,” separately from the later execution state.
4. Keep the lane blocked or paused for immediate assertions, then unblock it and invoke the real scheduler.
5. Assert the scheduler alone performs `todo → in_progress`, sends the pending input, and reuses the latest valid session/run identity rather than creating an unrelated conversation.
6. Use a request counter or channel around the test provider to distinguish “not called yet” from “eventually called.” Avoid sleep-only assertions; wait with a bounded timeout and inspect persisted final state.

This applies to job boards, sequential automation lanes, durable agent queues, and any UI where “sent” means accepted for later processing rather than already running.

## Test-run artifact hygiene

Browser and end-to-end test runners may rewrite tracked reports or create screenshots, traces, result directories, and HTML reports even when the product test passes. Before staging or reporting completion:

1. Compare `git status` before and after verification.
2. Restore only runner-generated changes that were clean at the start; never erase pre-existing dirty files.
3. Prefer runner flags or configuration that suppress persistent reports for focused verification when available.
4. Stage explicit product and regression-test paths rather than `git add .`.
5. Recheck `git status` after commit or deployment so generated evidence is not accidentally presented as unrelated user work.

## Concurrent shared-checkout commits

A shared checkout may advance or become dirty while verification and deployment are in progress. Treat this as normal concurrency, not permission to absorb or erase another worker's changes. Record the baseline SHA before launching any autonomous coding CLI, even when its prompt says not to commit or push. After it exits, compare `HEAD`, the tracked remote, and that baseline before inspecting only `git diff`: an autonomous commit can make the working tree look clean while hiding both intended changes and scope creep in history. If this happened, review the full baseline-to-HEAD range, preserve the implementing commit, and apply a narrow corrective commit rather than resetting shared history.

When task-owned edits are interleaved with unrelated concurrent changes in the same files, stop trying to stage the dirty checkout. Reproduce only the approved delta in a clean branch worktree, verify there, and deploy that clean artifact. Follow `references/task-only-clean-worktree-delivery.md` for the exact sequence and evidence boundaries.

1. Capture the task commit SHA immediately after committing and use that immutable SHA in subsequent verification and reporting; do not assume `HEAD` will still identify the task later.
2. Stage only explicit task paths. Immediately before commit, inspect the staged diff and confirm no concurrent files are included.
3. Never restore, reset, amend, or clean files merely because they appeared after the task's initial status snapshot. Restore only artifacts proven to have been generated by your own command and clean before that command.
4. After pushing, verify the task commit is contained in the tracked remote branch (for example, `git branch -r --contains <task-sha>`). Equality between local `HEAD` and the remote tip is unnecessary when a later valid commit has landed.
5. If `HEAD` advances after your commit, report the task's own SHA and say it is pushed/contained upstream. Do not misreport the newer `HEAD` as your commit, and do not claim the checkout is clean when unrelated concurrent work remains.
6. Tie deployment evidence to the served artifact or behavior, not merely to the current checkout tip; a later commit may legitimately include the task change plus unrelated work.
7. Re-read task paths immediately before post-commit verification. If they differ from the task commit because another worker edited or reverted them, do not verify the mutable checkout as though it represented the pushed task, and do not silently restore or commit over concurrent work. Verify the immutable task SHA in a temporary clean worktree; report shared-checkout divergence separately. Integrate only when ownership and the intended combined scope are known.
8. When the workspace verifier requires a directly observed `hermes-verify-*` run but concurrent edits break the shared checkout, create both the script and a detached worktree with `mktemp`, attach the worktree at the exact task SHA, and run the focused regression plus proportionate build from that worktree inside the script. Execute the script directly and clean both artifacts with a trap. Label the result “ad-hoc targeted verification against immutable commit `<sha>`”; it does not prove the concurrently edited checkout is green.
9. If the first ad-hoc run fails because tests reference fields/functions present only in another worker’s unfinished half-edit, inspect status/diff to classify shared-checkout divergence. Do not patch, revert, or stage that work merely to make verification pass; rerun against the immutable task SHA.

For code-split SPAs, the entry HTML often names only the entry bundle, not the changed route's lazy chunk. Resolve the route chunk from the built manifest/import graph or deployed assets, then probe that exact chunk for a stable semantic marker. An entry-bundle hash or HTTP 200 alone does not prove the changed route was deployed.

When a user reports production behavior after work originated in a preview branch, establish the reported deployment target before editing or redeploying. A preview repair is not a production fix, and a fix SHA absent from the production branch may still have been squashed or reimplemented upstream. Compare ancestry, deployed artifact, runtime API target, and exact authenticated behavior. For intent-sensitive booking/checkout redirects, follow `references/deployment-target-and-booking-flow-proof.md`; source strings and focused tests remain supporting evidence until the real production browser flow reaches the expected destination and focus target.

For isolated SPA previews, also read `references/spa-preview-prefix-and-browser-evidence.md`. It covers emitted-prefix discovery, public asset/MIME probes, the boundary between transport checks and browser-render evidence, screenshot validation, and staging untracked files. Add the explicit preview web-server location before browser verification: a production catch-all can serve the preview file while injecting conflicting production basename/API globals, so inspect the final public HTML for duplicate runtime injections and require the rendered route—not HTTP 200—to confirm routing. For typography work, pair the screenshot with public-page computed `font-family` and loaded-font checks because appearance alone cannot prove the exact face. When the preview includes uploaded media, attendee avatars, or checkout, also read `references/subpath-preview-media-and-checkout.md` for preview-aware `/uploads/` routing, end-to-end profile-picture contract checks, explicit test-payment finalization, and the Vite build-base trap. If a previously verified preview appears to regress, read `references/preview-mount-persistence-and-checkpointing.md` before changing application code: prove the public URL still serves the isolated basename, API base, asset prefix, Nginx mount, and filesystem artifact. That reference also defines checkpoint-commit handling for long-lived preview worktrees.

For manager-request/admin-approval session workflows, also read `references/session-approval-preview-e2e.md`. It defines generated-versus-persisted approval invariants, the dual-role endpoint trap, persisted public E2E, notification-dropdown deep links including legacy rows, mobile calendar scrolling, and truthful active-work status labels.

For admin create/edit forms, verify dirty-state behavior across the actual navigation surfaces, not only the form component: pristine forms must leave without prompting; changed forms must prompt on breadcrumb, cancel, dashboard tab/link navigation, and browser unload; successful saves must clear the guard. Nested image or package controls may mutate state outside ordinary text-input events, so test their dirty-state propagation explicitly. If a navigation item must be hidden, inspect and assert every navigation provider (for example both a horizontal tab list and a workspace/sidebar builder) while preserving the route unless deletion was requested. Native numeric input attributes are UX only: mirror integer, money, and quantity limits in frontend submit validation and the current API boundary, with tests at the maximum and one value above it.

## Headless Chromium and ARM64 browser fallback

When the primary browser runner cannot provision its bundled browser—especially on Linux ARM64 where Chrome-for-Testing builds may be unavailable—do not downgrade authenticated E2E to HTTP checks. Use the system Chromium executable with `playwright-core` (which does not download a browser):

1. Probe the installed executable (`/snap/bin/chromium`, `/usr/bin/chromium-browser`, or equivalent); do not hardcode one path across hosts.
2. In a temporary directory, install `playwright-core` only and launch with `chromium.launch({executablePath: '<system-path>', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage']})`.
3. Exercise the exact public authenticated flow, collect `console` and `pageerror` events, assert the persisted terminal state, and save a screenshot.
4. Keep temporary browser dependencies and credentials outside the repository; never commit test credentials.
5. Prefer public setup flows for prerequisite records. If none exists, create a uniquely named dedicated E2E tenant and the minimum fixture in the actual runtime database, respecting effective schema, ownership, and tenant IDs. Inspect the live schema first rather than trusting planning documents. The browser must still perform the feature's actual writes and transitions through the public UI/API; direct fixture setup is not itself E2E evidence.

A browser package provisioning failure is setup state; the durable fallback is pairing `playwright-core` with an already-installed system Chromium.

## Headless Chromium artifact classification

When the primary browser runner is unavailable, Chromium headless may create a valid screenshot or DOM dump and still return non-zero because of host GPU, D-Bus, or accessibility-bus warnings. Do not let `set -e` discard that evidence before classifying the run:

1. Capture exit status and stderr separately while preserving the requested artifact.
2. Confirm the screenshot/DOM file exists and is non-empty.
3. Inspect stderr for page/runtime failures (`Uncaught`, console errors, `net::ERR`) separately from host-integration warnings.
4. Visually inspect the screenshot or parse the DOM, then report the host warning and render result as distinct boundaries.

A non-zero browser exit is not a passing render by itself, but neither does it invalidate a demonstrably complete artifact.

## Side-effect-free auth and routing verification

For authenticated production multipart/import endpoints, use `references/authenticated-backend-upload-e2e.md`: preflight usable credentials before deployment, proxy the exact route prefix, and prove both persistence and absence of forbidden downstream side effects. Do not treat a public `401` as authenticated E2E.

When debugging signup/login routing, do not create or delete user accounts merely to infer whether the frontend reached the backend. Trace submit handler → API URL construction → browser network status/body → reverse-proxy access log → proxy mapping → global middleware → route handler first. Reproduce the browser's `Origin`, `Host`, credentials mode, and public path: a curl without `Origin` can return 201 while the browser is rejected by CORS before the handler.

Prefer non-mutating or already-existing-state probes. For example, an existing identity returning `409 user_exists` proves a same-origin request crossed proxy and CORS and reached registration without creating data. Pair it with an unrelated-origin probe that must remain `403 origin_not_allowed`. Report the exact failing boundary and response; never infer “the request did not reach the API” from generic frontend copy or sparse application logs.

For authenticated browser E2E using an existing session, inspect the frontend auth source before injecting credentials. A server session cookie can authenticate direct API calls while the SPA still renders logged out because its client session is bootstrapped from local storage or another client-side store. Seed every contract the real client requires (for example both cookie and token/user local-storage keys) before navigation, then prove the rendered authenticated chrome appears before exercising the feature. Use the active locale when locating translated controls: prefer an accessible-name regex covering supported labels or first inspect the rendered modal text, rather than hard-coding one locale and misclassifying a locator timeout as a feature failure.

## Go SQLite single-connection generators

For Go endpoints that read candidate rows and then insert notifications, reminders, queue items, or summaries with `MaxOpenConns(1)`, verify that all query rows are consumed and explicitly closed before any write. Raising the connection limit can mask the defect. Require timeout, idempotency, `db.Stats().InUse`, subsequent authenticated-request, and public deployment assertions. See `references/go-sqlite-single-connection-generation.md`.

## Pitfalls

- Do not cite test/build output produced before the final edit.
- Do not use a predictable fixed filename under `/tmp`.
- Do not leave temporary verification artifacts in the repository.
- Do not claim deployment verification from a local test alone; probe the served artifact separately when deployment is part of the task.
- Do not equate a public HTML asset-name match with behavioral verification unless the deployed bundle is tied to the verified commit or the actual flow was exercised.
- For interactive form changes, a public HTTP 200, matching bundle hash, unit tests, and build still do not prove the requested flow. Exercise the exact public state transition (default selection, conditional fields, submission, persisted result) before calling it completed. If browser E2E is blocked, report “implemented and deployed; public E2E pending” rather than “completed,” and keep trying an available browser path before finalizing.
- Do not chain static deployment and service replacement in a way that obscures partial success. Verify the destination `index.html` after the final copy, verify the service’s discovered runtime port after restart, and report each boundary independently.
- When promoting an approved preview from a dirty production checkout, use a clean integration worktree and build the squash commit there. Runtime-only files in the preview worktree (databases, uploads, generated binaries) make cleanup non-destructive: remove the public route/assets/process, but preserve the dirty worktree rather than force-removing it.
