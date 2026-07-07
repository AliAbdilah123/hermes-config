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
- Standalone styled HTML with readable typography, table of contents for long plans, responsive layout, and styled code blocks.
- Store under the relevant project path when known, e.g. `<project path>/docs/<slug>.html`.
- Publish it at the project's public domain PRD path (for Komuna, `https://komuna.ahsanworks.com/prd/<name>.html`) via the web server PRD symlink directory; avoid raw IP links unless the user explicitly asks for them.
- Verify local/public HTTP 200 before finalizing.
- End the final response with the public link.

If the task is code-related, include exact file paths, likely test targets, and verification steps.

## Save location

Save the plan with `write_file` under:
- `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`

Treat that as relative to the active working directory / backend workspace. Hermes file tools are backend-aware, so using this relative path keeps the plan with the workspace on local, docker, ssh, modal, and daytona backends.

If the runtime provides a specific target path, use that exact path.
If not, create a sensible timestamped filename yourself under `.hermes/plans/`.

## User-specific public review artifact

For this user, a plan intended for review should not remain markdown-only. After saving the markdown plan:

1. Render a styled, readable HTML version with a table of contents and code-block styling.
2. Store the canonical HTML under the relevant project path at `docs/<name>.html` when a project path exists.
- Publish it at the project's public domain PRD path (for Komuna, `https://komuna.ahsanworks.com/prd/<name>.html`) via the web server PRD symlink directory; avoid raw IP links unless the user explicitly asks for them.
- Verify local/public HTTP 200 before finalizing.
5. If the user answers open questions in the plan, update both the markdown plan and the public HTML before implementing.

Use the `claude-design` skill/reference workflow for the publication mechanics.

## Interaction style

- If the request is clear enough, write the plan directly.
- If no explicit instruction accompanies `/plan`, infer the task from the current conversation context.
- If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
- When the user asks to "ask clarifying questions as you go" but also requests a reviewable plan/design before implementation, include a visible **Open Questions for Approval** section in both the markdown plan and HTML review artifact. Ask only the questions that block design approval; do not interrupt with low-stakes questions before producing the review artifact.
- If the user asks not to implement until approval, add an explicit **Implementation Gate** section to the plan/artifact and final response. Do not treat plan approval, route-label answers, or design-choice answers as deployment permission unless the user explicitly says to implement.
- If the user corrects the proposed design or answers design options, update the plan/review artifact and wait for explicit implementation/deployment instruction; do not treat design-choice answers as permission to deploy.
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

### Mobile/responsive UI fix plans need concrete viewport strategy

When the user asks for a design plan before fixing a responsive/mobile UI bug, make the review artifact useful as an approval surface rather than a generic task list. Inspect the relevant components first, then include:
- the suspected desktop-first causes (fixed/min heights, oversized padding, wide grids, large typography/cards, overflow risks),
- the exact breakpoint strategy (desktop/tablet/mobile) and what changes at each width,
- the smallest likely implementation path (prefer CSS/media-query overrides and class hooks before component rewrites),
- validation at named viewport widths plus no-horizontal-overflow and console-error checks,
- an explicit implementation gate if the user asked for the plan before live fixes.

Keep this class-level: do not encode a single project's file paths unless they are examples inside the plan itself.

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
