---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, plan, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 4a. SPA Auth UI / Build-Time Env Triage

When a deployed Vite/React auth route shows the wrong login experience (fallback/basic form instead of provider UI) or a partial provider UI (for example only a card separator/strip line):
- Inspect **build-time frontend env at the app build root**, not just the repository root env. Vite only exposes `VITE_*` vars at build time and auto-loads env files relative to the directory running `vite build`.
- Verify the **served bundle** contains the expected provider URL/config and not an `undefined`/fallback expression. Source files and `.env` are not enough evidence.
- Check provider UI prerequisites: required CSS import and context/provider wrapper. For Neon Auth UI, `<AuthView />` needs `@neondatabase/auth-ui/css` (or Tailwind variant) and `NeonAuthUIProvider` with the Neon auth client; otherwise it may render only a skeleton/separator.
- Verify with rendered DOM markers for real fields/buttons (`Sign In`, `Email`, `Password`) after deploy, not just HTTP 200 or asset presence.

See `references/vite-spa-auth-ui-triage.md` for the detailed checklist and verification recipe.

### 4b. OAuth/App-ID Error Triage

When a user reports a social login/OAuth "Invalid App ID" or "app id error" after updating env:
- Inspect the **running service environment**, not just repository env files. For systemd, find `EnvironmentFile=` and compare it to `/proc/<pid>/environ` with values masked.
- Generate the deployed OAuth start URL and parse provider URL parameters safely: app/client id length and last 4 chars, redirect URI, scopes, provider host/path.
- Check for stale project paths in `redirect_uri`, frontend base URL, and provider cancel URLs.
- If multiple env aliases exist for the same app id, prefer canonical provider ids (e.g. `META_APP_ID`/`FACEBOOK_APP_ID`) over legacy product-specific aliases that may contain stale or secret-shaped values.
- Verify by fetching the provider dialog with redirects enabled and confirming it no longer contains the invalid-app-id page and reaches login/oauth flow.

See `references/oauth-provider-env-precedence.md` for the detailed recipe and fix pattern.

### 4b. Vite Frontend Env Missing After Deploy

When a Vite/React production page renders a fallback UI instead of a provider integration (auth widget, analytics, payment, etc.) even though the repo has the right env values:
- Inspect the **compiled deployed JS bundle**, not just source files or root `.env`. Search for the expected provider URL/domain and for inlined-undefined patterns like `(void 0)?.trim`.
- In monorepos, confirm where the build runs. Vite auto-loads env files from the Vite app root (`envDir`, default current app root), so a repo-root `.env` may be ignored by `apps/web` builds.
- Put `VITE_*` values in the app root env file, export them during the build, or configure `envDir` intentionally.
- Rebuild and publish the new hashed `dist/` asset, then fetch the public HTML/JS to verify the provider literal is present and the old undefined expression is gone.

See `references/vite-deployed-env-triage.md` for a compact reproduction/fix recipe.

### 4b. SPA Subpath API Routing

When a deployed SPA lives under a subpath (for example `/projects/<app>/`) and login or API actions show generic `request_failed` while the backend is healthy:
- Compare the root-relative API URL (`/api/v1/...`) against the mounted proxy URL (`/projects/<app>/api/v1/...`). A root-relative request can bypass the app's Nginx location and return 404 or hit the wrong service.
- Inspect the **served production JS bundle** for API URL construction. A source helper may use `import.meta.env.BASE_URL`, but code like `path.startsWith('/api/') ? path : apiPath(path)` silently skips the base path for the exact API routes that need it.
- Fix at the API-path helper so all API calls normalize through the base-aware route builder; do not patch individual login calls only.
- Verify with browser/network evidence that login, `/me`, and post-login workspace/data requests all target `/projects/<app>/api/...` and return 200.

See `references/spa-subpath-api-routing.md` for the detailed checklist and fix pattern.

### 4c. Browser FFmpeg / Video Export Performance Triage

When a browser video editor/export flow feels slow:
- Inspect the **actual generated FFmpeg arguments** before proposing platform rewrites. Full re-encode flags (`-c:v libx264`, `-c:a aac`, CRF/preset) are usually the bottleneck; `-c copy` is a fundamentally different fast path.
- Check seek placement. `-i input -ss START` favors accurate output but can decode extra frames; `-ss START -i input` is much faster and often sufficient for fast/keyframe-near cuts.
- Check whether each slice is exported as a separate sequential job and whether the whole source file is copied into a browser/WASM virtual filesystem.
- Benchmark fast-copy, exact re-encode, and fast-seek re-encode variants with a representative source before recommending native mobile or server architecture.
- Prefer a product fix that exposes modes: **Fast Export** (input seek + stream copy) by default, **Exact Export** (frame-accurate re-encode) as the slower option, and server-side/native FFmpeg for long videos or batch reliability. Native Android can help, but it is not the root fix if the algorithm still re-encodes every clip sequentially.

See `references/browser-ffmpeg-export-performance.md` for command patterns, benchmark setup, and a fix decision tree.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### 4d. SQLite Runtime DB Deleted / Misleading Auth Errors

When a deployed SQLite-backed app suddenly reports duplicate-user errors for brand-new signup attempts, or login succeeds but the next session check is `null`:
- Inspect the running service's configured DB path and the process file descriptors before restarting. If the DB was deleted while open, `/proc/<pid>/fd` may show `app.db (deleted)`.
- Recover the live DB from the open file descriptor before restart, then restore the configured runtime DB path with correct ownership.
- Treat this as two bugs: runtime data-path loss plus auth error masking. Fix auth handlers so only unique constraint failures return `USER_ALREADY_EXISTS`; generic DB/session failures should return explicit 500 errors and must not be ignored.
- Verify with direct public-route signup, session, signout, login, and session checks using a cookie jar.

See `references/sqlite-runtime-db-recovery-and-auth-errors.md` for commands and the full recovery/fix recipe.

### 5a. Frontend/API Shape Drift (`.filter` / `.map` is not a function`)

When a React/Vite page shows a runtime collection error such as `t.filter is not a function`:
- Trace the value back to the `apiClient.get<T>()` boundary; the generic type may not match runtime JSON.
- Probe the real deployed/local endpoint and inspect the top-level JSON shape. A common mismatch is frontend expecting `Item[]` while the API returns `{ data: Item[] }` or a paginated envelope.
- Fix with a small typed response normalizer/unwrap helper at the API consumption boundary, not by hiding the symptom with optional chaining around array methods.
- Add a regression test whose mock uses the real API envelope shape that previously failed.
- Verify the targeted test, build/typecheck, and if deployed, fetch the served bundle/API to confirm the deployed artifact includes the normalizer and the endpoint shape is understood.

See `references/frontend-api-shape-drift.md` for a compact recipe and minimal TypeScript pattern.

### 5b. UI Metric vs. Global Data Count Questions

When a user asks whether a displayed count (for example `18/18 TAKEN`, badge counts, usage counters, quota indicators) implies a global entity count:
- Treat the screenshot as a symptom label, not proof of the underlying data model. Identify the UI field's source before answering.
- Distinguish **scoped operational metrics** (session seats taken, pending approvals for one program, per-product capacity) from **global records** (registered users, program members, claims/bookings across the site).
- Inspect the runtime state or API response that feeds the screen and separately count the relevant global table/list. If the app uses a mock/blob state store, parse the blob and report both the stored display metric and the actual backing records visible in that store.
- If a displayed count is seeded/demo aggregate data rather than derived from individual records, say so explicitly; do not imply that each unit has a visible row unless verified.
- Final answer should be concise: “X means scoped metric A, not global count B; verified global count is N; caveat if demo/seeded aggregate.”

### 5c. SQLite JSON-State Role Seeding / Demo Admin Access

When a SQLite-backed app stores auth records in normal tables but product/domain state in a JSON blob (for example `app_state.payload`) and users appear to gain admin/manager dashboards unexpectedly:
- Inspect auth tables and JSON blob state separately. `auth_users`/sessions answer who can log in; JSON `Members`/`Roles` often answers what dashboards they see.
- Preserve existing auth identities while seeding: upsert by email/id, then assign them into programs in the blob. Do not overwrite existing users with fixture-only accounts unless requested.
- Search for fallback workspace/access code that grants default admin/superadmin roles when unauthenticated, no membership exists, or a dev user is active. If present, remove/fix the fallback; changing roles in seed data will not solve automatic admin access.
- Back up the DB before rewriting the JSON blob, then verify role aggregates and real signed-in `/me/workspace` responses for the intended manager, ordinary user, and superadmin.
- See `references/sqlite-json-state-role-seeding.md` for the compact recipe and verification checklist.

### 6. External OAuth Provider Errors

**WHEN a social login/connect flow fails with provider errors (Meta/Facebook/Instagram, Google, etc.):**

- Separate app-generated URL bugs from provider-dashboard configuration issues.
- Parse the generated OAuth URL and verify `client_id`, `redirect_uri`, scopes, and provider version/path.
- Compare environment aliases and precedence; stale legacy env names can silently override the intended app id.
- Probe the provider authorization URL directly with `curl -L -A 'Mozilla/5.0'` and inspect effective URL/body for provider-specific errors.
- If app id is accepted but provider says the app is inactive/not available, stop code changes and check provider dashboard mode, roles/testers, products, and permission approval.

For Meta/Facebook-specific diagnostics, see `references/meta-oauth-app-id-active-status.md`.

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

### Responsive UI Regression Notes

When the issue is a responsive layout regression, especially one described as "not responsive like the original":
- First identify shared layout components used by all affected routes; fix the shared component before duplicating route-level tweaks.
- Compare against the original/reference implementation, but convert fixed inline dimensions/positions into breakpoint-aware classes rather than restoring rigid values.
- Verify both the component and its parent wrapper; a responsive child can still fail if the parent is hidden at the wrong breakpoint or uses height classes without a concrete containing height.
- For data-heavy tables that overlap or clip on phones, inspect fixed table widths, long unwrapped cell contents, and horizontal-scroll state. Prefer a mobile card presentation below phone breakpoints while preserving desktop tables. See `references/responsive-data-table-mobile-cards.md`.
- Use screenshot-based viewport checks after implementation. See `references/responsive-ui-regression-qa.md` for a compact recipe, including Vite base-path and Chromium `--virtual-time-budget` tips.

### SPA Auth Provider / Login UI Notes

When a deployed SPA shows the wrong login UI (hosted provider UI, basic fallback, missing OAuth button, or a skeleton/strip instead of a form):
- Confirm the intended auth mode before fixing. Do not assume OAuth/hosted auth is desired just because provider env vars exist; the correct product requirement may be first-party/local login.
- Check build-time frontend env scope, not just root env files. Vite only inlines `VITE_*` variables visible to the frontend build process; nested apps may not load a repository-root `.env`.
- If enabling a third-party auth UI, verify the required provider/context wrapper and CSS import, not only the page component.
- If reverting to local/basic auth, remove temporary frontend env files such as `apps/web/.env.local` before rebuilding so the deployed bundle does not keep selecting the hosted provider path.
- Verify the public deployed artifact with a cache-busted URL and DOM/text markers for both intended labels present and unintended provider labels absent.
- See `references/spa-auth-provider-env-and-fallbacks.md` for a compact checklist.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
