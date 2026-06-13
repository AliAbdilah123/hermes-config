---
name: tdd
description: "Test-driven development with RED-GREEN-REFACTOR, tests before code, vertical slices, and integration-style verification."
tags: [testing, tdd, red-green-refactor, development, quality]
related_skills: [test-driven-development, systematic-debugging, writing-plans, subagent-driven-development]
---
# Test-Driven Development

## Overview

Tests-first, behavior-focused development with strict RED-GREEN-REFACTOR discipline.
Integrates the generic RED-GREEN-REFACTOR rules from `test-driven-development` with the
vertical-slice discipline from the older standalone `tdd` skill.

## When to Use

- New features, bug fixes, refactors, or behavior changes
- Any change where behavior must be verified before merging
- Workflows that need automated regression protection

## Iron Law

NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.

Write code before the test? Delete it. Start over. No exceptions without explicit user approval.

## Core Loop (Vertical Slices)

Wrong: horizontal RED → GREEN batches.
Right: one test → one implementation → repeat.

Each behavior is one vertical slice:
1. Write one failing test for one behavior.
2. Run it and confirm it fails for the expected reason.
3. Write the minimal implementation to pass.
4. Run to verify pass.
5. Refactor if needed, keeping tests green.
6. Commit.

## Test Quality Rules

- One behavior per test.
- Use public interfaces; tests should survive internal refactors.
- Prefer real behavior over mocks; mocks only when unavoidable.
- Descriptive names that state behavior, not implementation.

## Common Anti-Patterns

- Writing all tests first, then all implementation.
- Tests that pass immediately (tests-after anti-pattern).
- Testing implementation details instead of behavior.
- Keeping code written before tests as "reference."

## Integration

- For deeper RED-GREEN-REFACTOR enforcement, load `test-driven-development`.
- For vertical slice discipline and tracer-bullet guidance, follow the workflow in this skill.
- When fixing bugs, use `systematic-debugging` to find root cause first, then a reproducing test, then fix.
