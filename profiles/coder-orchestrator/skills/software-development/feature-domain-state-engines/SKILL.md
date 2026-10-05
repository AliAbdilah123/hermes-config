---
name: feature-domain-state-engines
description: Use when implementing reusable deterministic domain engines for localized transaction capture, recursive habit progression, nested productivity planning, or invariant-preserving directed graphs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, state-engine, finance, habits, tasks, graphs]
    related_skills: []
---
# Feature: Domain State Engines

## Localized transaction capture
Parse locale vocabulary and amount multipliers into integer minor units, validate owned accounts/categories, then require parse -> review -> submit. Deterministic parsing must not be presented as AI.

## Recursive habits and goals
Store reusable habit definitions by ID; goal nodes reference them. Recursive aggregation deduplicates IDs. Auto defaults carry provenance and explicit override/undo. Level changes append immutable history and do not rewrite existing daily check-ins.

## Nested planning
Persist goals, task groups, parent task IDs, habits/logs, energy readings and focus plans. Replace-all child updates transact and reject ownership violations/cycles. Hierarchy rendering tolerates missing parents and keeps stable ordering.

## Directed graphs
DB constraints reject self/duplicate edges and scope nodes/edges to workspace/project. Project creation bootstraps start/end atomically. Splitting an edge replaces it with two edges while preserving downstream metadata.

## Templates
- `templates/domain-invariants.ts`
- `references/finance-habits-tasks-graphs.md`

## Pitfalls
Direct writes from parser; floating money; duplicate recursive IDs; overrides without provenance; schema-source drift; stubbed subtask persistence; client-only workspace isolation; graph integrity only in React.

## Verification
Locale fixtures, ownership/integer money, recursive dedupe, override undo, immutable history, cycle prevention, hierarchy recovery, transactional bootstrap, and edge split invariants.

## Provenance
`arus-ai`, `habit-realm`, `self-flow`, and `endstate`. Only code-proven portions are templates; unfinished persistence remains explicitly excluded.
