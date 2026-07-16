---
name: plan
description: "Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code."
version: 2.0.0
author: Hermes Agent (writing-craft adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, plan-mode, implementation, workflow, design, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Plan Mode

Use this skill when the user wants a plan instead of execution.

## Core behavior

For this turn, you are planning only.

- Do not implement code.
- Do not edit project files except the plan markdown file.
- Do not run mutating terminal commands, commit, push, or perform external actions.
- You may inspect the repo or other context with read-only commands/tools when needed.
- Your deliverable is a markdown plan saved inside the active workspace under `.hermes/plans/`.

## Output requirements

Write a markdown plan that is concrete and actionable.

Include, when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

If the task is code-related, include exact file paths, likely test targets, and verification steps.

## User-facing review artifact requirement

For this user, a plan or document produced for review should not remain markdown-only. After saving the markdown/source plan, also create a styled HTML review artifact and publish it at a public link. Follow `references/review-doc-html-publication.md` for the docs-path/symlink/public-URL workflow and verification checklist.

Minimum expectations:
- Standalone styled HTML with readable typography, table of contents for long plans, responsive layout, styled code blocks, and a dark-theme-first visual design.
- Include a working light/dark mode toggle in every plan/review HTML artifact. Default to dark mode, persist the user's choice with `localStorage`, and keep the artifact readable without external JS/CSS.
- When a task needs both an implementation plan and UI/design visualization, publish them as **separate pages**: one plan page for implementation tasks and one design page for static visual mockups. Cross-link the two pages. Do not combine long task plans and visual mockups into one overloaded page.
- Match the reviewed project's actual visual system in design artifacts. Inspect the current page/components/CSS first, then reuse the app's layout pattern, tokens, typography, spacing, and navigation reality. Do not invent a sidebar/topbar/shell that the current page does not have. See `references/ui-redesign-review-artifacts.md` for the detailed checklist and pitfalls.
- Store under the relevant project path when known, e.g. `<project path>/docs/<slug>.html`.
- Publish it at the project's public domain PRD path (for Komuna, `https://komuna.ahsanworks.com/prd/<name>.html`) via the web server PRD symlink directory; avoid raw IP links unless the user explicitly asks for them.
- Verify local/public HTTP 200 before finalizing.
- End the final response with the public link.

If the task is code-related, include exact file paths, likely test targets, and verification steps.

## Save location

Before choosing a document path or public domain, verify that the document actually belongs to the presumed project. A project mentioned in server configuration, memory, nearby files, or an available publication route is not evidence of affiliation.

- When a related project is established, save the canonical plan in that project's `.hermes/plans/` or `docs/` directory as appropriate.
- When no related project exists yet, save review documents under the user's home-level `~/docs/` collection. Do not place or brand them under an unrelated project's directory, domain, theme, or route merely because that route is convenient.
- If project affiliation is ambiguous, use the neutral home-level location and neutral publication route by default; move it into a project only after affiliation is established.

For workspace-bound implementation plans, save with `write_file` under:
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

Treat that as relative to the active working directory / backend workspace. Hermes file tools are backend-aware, so using this relative path keeps the plan with the workspace on local, docker, ssh, modal, and daytona backends.

If the runtime provides a specific target path, use that exact path.
If not, create a sensible timestamped filename under the applicable location above.

## User-specific public review artifact

For this user, a plan intended for review should not remain markdown-only. After saving the markdown plan:

1. Render a styled, readable HTML version with a table of contents and code-block styling.
2. If the work includes UI/design approval, render the plan and the design/mockup as separate HTML pages, e.g. `docs/<slug>-plan.html` and `docs/<slug>-design.html`, with cross-links.
3. Store the canonical HTML under the relevant project path at `docs/<name>.html` when a project path exists.
- Publish it at the project's public domain PRD path (for Komuna, `https://komuna.ahsanworks.com/prd/<name>.html`) via the web server PRD symlink directory; avoid raw IP links unless the user explicitly asks for them.
- Verify local/public HTTP 200 before finalizing.
5. If the user answers open questions in the plan, update the markdown plan and all relevant public HTML pages before implementing. Move answered items into a visible **Confirmed decisions** section, remove or shrink the resolved **Open Questions** section, and verify the public artifact contains the exact new decision phrases before replying.

Use the `claude-design` skill/reference workflow for the publication mechanics.

## Interaction style

- If the request is clear enough, write the plan directly.
- If no explicit instruction accompanies `/plan`, infer the task from the current conversation context.
- If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
- When the user asks to "ask clarifying questions as you go" but also requests a reviewable plan/design before implementation, include a visible **Open Questions for Approval** section in both the markdown plan and HTML review artifact. Ask only the questions that block design approval; do not interrupt with low-stakes questions before producing the review artifact.
- When the user describes a new diagram/canvas planning app, produce a PRD-style plan first: define graph semantics, node/edge mutations, linked-object behavior, MVP cuts, data model, API shape, and acceptance criteria before implementation. See `references/greenfield-diagram-app-prd.md`.
- If the user asks not to implement until approval, add an explicit **Implementation Gate** section to the plan/artifact and final response. Do not treat plan approval, route-label answers, or design-choice answers as deployment permission unless the user explicitly says to implement.
- If the user corrects the proposed design or answers design options, update the plan/review artifact and wait for explicit implementation/deployment instruction; do not treat design-choice answers as permission to deploy.
- If the user says a previous design was better or approves a visual style, preserve that design as the baseline. When later requirements are textual/spec-level, update the plan first and add only minimal callouts/labels/disabled states to the design page; do not rewrite the design page from scratch.
- For mobile/UI design work, when the user says the design is not visible or unchanged, update and republish the styled review artifact first; do not silently patch or deploy the app. Provide the public review URL and explicitly state whether it is a static design preview or the live site.
- After saving the plan, reply briefly with what you planned and the saved path.

---

# Writing the Plan Well

The rest of this skill is the craft of authoring a *good* implementation plan — the content that goes inside the markdown file above.

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

## When a Full Implementation Plan Helps

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## Plan Document Structure

### Header (Required)

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Writing Process

### Step 1: Understand Requirements

Read and understand:
- Feature requirements
- Design documents or user description
- Acceptance criteria
- Constraints

### Step 2: Explore the Codebase

Use Hermes tools to understand the project:

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

### Step 3: Design Approach

Decide:
- Architecture pattern
- File organization
- Dependencies needed
- Testing strategy

### Step 4: Write Tasks

Create tasks in order:
1. Setup/infrastructure
2. Core functionality (TDD for each)
3. Edge cases
4. Integration
5. Cleanup/documentation

### Step 5: Add Complete Details

For each task, include:
- **Exact file paths** (not "the config file" but `src/config/settings.py`)
- **Complete code examples** (not "add validation" but the actual code)
- **Exact commands** with expected output
- **Verification steps** that prove the task works

### Step 6: Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:
```bash
git add [files]
git commit -m "type: description"
```

## Common Mistakes

### Bug-fix plans must start with the user's problem ledger

When the user asks for a plan before fixing bugs, especially with "write down the problems" or "don't implement before approval":
- Add a visible **Problems captured from the request** section near the top of both the markdown plan and public HTML artifact.
- Preserve the user's concrete complaint wording where useful, but translate it into actionable product risks (for example: misleading purchase surface, oversized layout, CTA route mismatch).
- Do read-only inspection only: code search, file reads, screenshots, existing tests. Do not edit app behavior, commit, deploy, or run mutating commands.
- Include **Current evidence from code inspection** separately from the problem ledger so symptoms, evidence, and proposed fixes do not blur together.
- End with an explicit **Implementation Gate** stating that approval of the plan/review artifact is not implementation permission unless the user explicitly says to implement.

### Mobile/responsive UI fix plans need concrete viewport strategy

When the user asks for a design plan before fixing a responsive/mobile UI bug, make the review artifact useful as an approval surface rather than a generic task list. Inspect the relevant components first, then include:
- the suspected desktop-first causes (fixed/min heights, oversized padding, wide grids, large typography/cards, overflow risks),
- the exact breakpoint strategy (desktop/tablet/mobile) and what changes at each width,
- the smallest likely implementation path (prefer CSS/media-query overrides and class hooks before component rewrites),
- validation at named viewport widths plus no-horizontal-overflow and console-error checks,
- an explicit implementation gate if the user asked for the plan before live fixes.

Keep this class-level: do not encode a single project's file paths unless they are examples inside the plan itself.

### Redesign proposals from supplied HTML/code need a visual review surface

When the user provides an HTML/CSS design reference and asks to redesign a page but approve the design before implementation:
- Treat the supplied code as composition/mood reference, not implementation source; do not paste CDN scripts, external theme config, or standalone demo scaffolding into the app plan.
- Inspect the current page/components enough to name the existing data flows, route/component boundaries, theme variables, and behaviors that must be preserved.
- Produce a public styled HTML review artifact that includes a static visual mockup/hero preview, not just prose. Make it obvious whether it is a static proposal or live site.
- Include a concise “borrow vs preserve” section: what layout ideas come from the reference, what current theme/system behaviors stay unchanged.
- Add an implementation gate and at least one explicit design choice if approval is needed; do not implement or deploy from the design-choice answer alone unless the user explicitly says to implement.

### UI redesign plans need separate plan and design pages

- When the user asks for a UI redesign plan, produce two separate public review pages by default:
- **Plan page**: implementation scope, file paths, task sequence, tests, risks, open questions, implementation gate.
- **Design page**: static visual mockup/prototype, interaction states, responsive states, and visual rationale.

Before authoring the design page, inspect the current app UI enough to avoid false structure. If the current page has no sidebar, the mockup must not show a sidebar. Reuse the project's actual theme tokens, typography, border radii, spacing, page width, and navigation pattern. The design page should look like the product being redesigned, not like a generic docs template.

Cross-link the pages prominently. Keep the plan page readable as a plan; keep the design page focused on visualization.

**Hard requirement:** Do not satisfy this by putting a mockup section inside the plan page only. If the work includes both implementation planning and visual design approval, publish and verify two distinct URLs before replying: `<slug>-plan.html` and `<slug>-design.html`. The plan page may link to the design page, but the design mockup must live on the separate design URL.

### Profile/account tab feature proposals need existing-tab parity

When the user asks for a new tab/section inside an existing profile, settings, dashboard, or account page and wants design approval first:
- Inspect the host page/component and one nearby existing page or route that already renders similar data before writing the proposal. Name the existing tab IDs, shell/card component, theme tokens, API endpoints, and tests likely to be reused.
- Propose the new tab in the same information architecture: sidebar order, panel shell, loading/error/empty states, and mobile behavior should explicitly mirror the current sibling tabs.
- Include a static visual mockup inside the public HTML artifact, not only a prose plan. The mockup should use representative rows/cards and the site's visual tokens so the user can approve look and structure.
- Keep the implementation plan frontend-only when an existing API already provides the data; call out backend/database changes only as conditional if the approved display fields are missing.
- Add an explicit implementation gate. Approval of the design or answers to display-choice questions is not permission to implement/deploy unless the user explicitly asks for implementation.

### Admin dashboard operations-tab plans need cross-role reuse and state-machine detail

When the user asks for a plan to redesign/add an admin dashboard operations tab that overlaps with manager/operator workflows (sessions, attendance, approvals, QR/check-in, bookings):
- Inspect the admin shell/nav/route and the closest existing role-specific implementation before writing the plan. Name the exact reusable components, adapter/mapping functions, API client methods, and route/controller endpoints already present.
- Prefer reusing role-specific components behind small props/adapters (for example disabling actions, relabeling status text, changing grouping) over rebuilding tables/cards. Call out the reuse target explicitly in the plan and mockup.
- Model time-sensitive behavior as a small state machine in the plan: inactive, upcoming, active/in-window, ended/finalized, locked/revoked. State which CTAs and mutations are enabled in each state and which timestamp/timezone source controls logic versus display.
- For program-level admin views that aggregate product-level manager data, plan the frontend-first path using existing endpoints, then add a conditional compact admin aggregation endpoint only if N+1 calls or role-scope auth makes reuse impractical.
- The public HTML review artifact should include a static visual mockup with the operational states represented (default inactive rows, an active expanded row, QR/window state, and a locked/completed example), not just the target prose.
- Include open questions for destructive or policy choices (for example deactivate support, label wording, adding a QR dependency), but keep implementation gated until explicit approval.

### Admin dashboard read-only history/support tab plans need existing API and support-triage checks

When the user asks for a missing admin dashboard tab that exposes historical/support data (purchases, payments, reports, issue queues, member activity):
- Inspect the real admin tab shell and route table first, then inspect the closest existing user/member/role-specific page that already displays the same data. Name the current tab insertion point and route path in the plan.
- Search for existing backend/API endpoints before proposing schema or controller work. If a program-scoped endpoint already exists, make the MVP frontend-first and call out backend changes only as conditional DTO enrichment.
- Design the first version as read-only support triage unless the user explicitly asks for mutations: search/filter, status pills, copy IDs, contextual links, empty/loading/error states, and enough identifiers to handle issue reports.
- Place the new tab according to domain flow, not alphabetically. For purchase-like flows, put purchase history between packages/products and generated artifacts such as vouchers.
- In the design artifact, mirror the current admin shell exactly (same top tabs, no invented sidebar) and show representative rows for success, pending/problem, and failed/refunded states.
- Include open questions for sensitive mutation policy (refunds, resolution labels, escalation workflows) and keep them out of MVP until explicitly approved.

### Existing drag/drop UI feature plans need flow preservation notes

When the user asks for a plan to extend drag/drop behavior in an existing UI, inspect the current drag/drop implementation before writing the plan. Include:
- the existing DnD library/context/handler names and why the plan reuses them instead of adding a package,
- the current data-shaping path (flat lists, grouped lists, parent chains, cached child records, etc.),
- explicit identity handling for moved items (for example, typed drag IDs when parent and child rows can share a droppable),
- how the plan preserves the current visual structure while allowing the new movement,
- the smallest persistence path (existing update/reorder API first; no backend/schema change unless required),
- acceptance checks that prove parent rows do not move when child rows are dragged and that refresh persistence works.

Default to cross-region movement first; defer same-region nested reordering unless the user explicitly asks for it.

**Critical: enumerate invariant props and filters.** When a shared UI component controls dual behavior through a single boolean prop (e.g., `hideSubtasks={!!parent}` controls both expand-button visibility AND nested-child rendering), the plan must explicitly name that prop and state whether it changes or stays. Generic language like "keep parent/subtask structure" is not enough — every implementation attempt will accidentally change the prop and break both behaviors. Similarly, when a useMemo filter decides which entries appear in the flat list vs. only nested, the plan must show the filter code and specify which condition changes (e.g., "remove only the `status === parent.status` guard, keep the rest"). Never draft a plan that says "preserve X" without naming the exact lines that preserve X.

### Feature breakdown requests need grouped implementation sections

When the user asks to "break down" an existing implementation plan "by feature" or "group the implementation plan on each feature," update the review artifact into feature-group sections instead of only adding more prose. Each feature group should include:
- outcome/capabilities,
- backend/data tasks,
- frontend/UX tasks,
- tests and acceptance checks,
- MVP/V1/V2 or other phase label.

Keep the original full-scope plan intact, but make it easier to review feature-by-feature. Update both the canonical markdown/source plan and the published styled HTML, then verify the public/cache-busted URL contains exact new feature headings.

### Over-narrowing a plan after recent corrections

When the user asks for an implementation plan "based on" an existing PRD/review artifact after a narrower correction was discussed, do not make the plan only about the latest correction. Re-read or inspect the source artifact and cover the full product scope: data model, backend/API, frontend UX, automation/jobs, integrations, testing, deployment, risks, and phased acceptance criteria. The recent correction should appear as one module or principle inside the broader plan, not as the whole plan.

### Vague Tasks

**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code

**Bad:** "Step 1: Add validation function"
**Good:** "Step 1: Add validation function" followed by the complete function code

### Missing Verification

**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths

**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Execution Handoff

After saving the plan, offer the execution approach:

**"Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"**

When executing, use the `subagent-driven-development` skill:
- Fresh `delegate_task` per task with full context
- Spec compliance review after each task
- Code quality review after spec passes
- Proceed only when both reviews approve

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious.**
