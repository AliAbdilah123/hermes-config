---
name: coding-standards
title: Shared Coding Standards
description: Hard constraints for code quality and Day One operability.
triggers:
  - code standards
  - one-engineer-archetype
  - stack rules
---

# Coding Standards

All coder profiles must follow these standards. Load alongside stack-specific skills.

## Scope

Shared standards for all coding profiles. Use the default stack unless the user explicitly specifies another.

## Non-Negotiable Standards

### 1. One Engineer Archetype
Work as one disciplined engineer, not a team of specialists. Produce one cohesive task branch, task-based commits, and inline tests first. Do not create half-built features, a frontend branch, or a backend branch that only compile but do not work end-to-end. The bar is Day One Operability: the code must build, start, and be demonstrable immediately.

### 2. Task-Based Commits
Commit working, test-bearing increments. Bad: "WIP", "fixes", "updates". Good: "feat: add login endpoint", "fix: resolve null users list", "test: cover auth middleware".

### 3. Refuse Fat Commits
Never check in one large commit that mixes signatures, schema migrations, handlers, and tests. Every commit must be one slice that a reviewer can read and approve without scrolling. Each slice must already pass the project’s unit and lint checks before moving on.

### 4. Keep Tests With Code
Unit and integration tests live next to the code they cover, in the same module or package. Do not shunt test files to a separate test tree. Shared test helpers can live under `internal/pkg/testutil` or equivalent.

### 5. Create Tests First
Follow RED-GREEN-REFACTOR. When implementing an endpoint, route, or reusable helper, write the test case that expresses the expected behavior and only then write the implementation.

### 6. Clarification Before Action
If any requirement is ambiguous or technically risky, stop and ask before reading or writing files. Do not perform read or write actions while waiting for the user to respond to a clarifying question.

### 7. File Search Before Creation
Use the search tool to check whether a file, config, or schema already exists before deciding to create or modify it.

### 8. Spec First
Prefer modifying agreed specs over diverging into implementation artifacts. Keep the spec/data model beside the source until done.

### 9. Small, Complete Fixes
Fix the real cause, not the symptom. Prefer surgical changes. If the change spreads beyond the task, pause and surface it.

### 10. Treat Agentless Environments As Normal
Code as if the next developer will read it without AI assistance. Write self-explanatory code, guard against ambiguity, and document tradeoffs inline.

### 11. Shared Code Should Be Pure and Explicit
Do not leak package internals across boundaries. Avoid `init()`, global state, and implicit mutations. Match input/output boundaries explicitly.

### 12. No Magic Dependencies
Do not introduce a library, framework, or toolchain without first explaining why it is needed and whether a lighter alternative would suffice.

### 13. Error Paths Are Cash
Handle the unhappy path first: timeouts, malformed responses, staleness, auth expiry, quota exhaustion, and partial writes. Surface what failed, why, and who it affects.

### 14. Preserve Existing Behavior
If current code works, do not change it without an explicit reason. Every change must have a user-visible purpose.

### 15. Review Before Delivery
Self-review every change before declaring success:
- Does it build?
- Does a naive reviewer understand the why?
- Is there a simpler way that avoids adding anything?

## Enforcement

- These standards apply to all coding tasks across all profiles.
- Corrections override guidance text if they come from the current user.
- Stack substitution requires explicit user approval.