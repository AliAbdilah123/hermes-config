---
name: product-implementation-audits
description: Evidence-based, read-only audits of an existing product against an approved MVP, PRD, business logic, roadmap, and canonical architecture.
---

# Product implementation audits

Use when asked what is genuinely complete, partial, missing, or broken in an existing repository. This skill governs read-only gap reviews, feature matrices, and MVP completion estimates.

## Core rule

Do not count a page, component, table, route, type, or test name as implementation. Trace each requirement through the real user path: frontend entry → API contract → authorization/validation → persistence → resulting state/activity → retrieval/rendering. Runtime behavior is strongest evidence when it can be exercised without violating the audit restrictions.

## Workflow

1. Read repository instructions and identify canonical product documents and architectural rules.
2. Capture the initial working-tree status.
3. Extract the requirements into a checklist using the user’s exact requested classifications and report sections.
4. Inspect schema, backend, frontend, permissions, tests, and cross-module contracts.
5. Run only side-effect-free checks allowed by the request.
6. Recheck working-tree status; never clean or alter pre-existing files.
7. Produce a conservative report focused on actual behavioral gaps and MVP blockers.

See [references/read-only-mvp-audit.md](references/read-only-mvp-audit.md) for the evidence ladder, exact status rubric, contradiction checks, compact row format, and completion-percentage guidance.

## Reporting style

When the user requests low token usage, keep citations exact and collapse repetitive requirements into compact tables. State audit/runtime limitations once, not under every row. Give details primarily for blockers, partial behavior, broken contracts, and architecture violations. Preserve the user’s required output order and exact labels.

For an inspection-first implementation request:
- Use the user's named sections as the report skeleton instead of adding a second generic hierarchy.
- For each domain, report only: existing reuse point, evidenced gap/root cause, minimum architectural change, and verification target.
- Do not repeat the full requirements or stream raw source/agent transcripts into the review response.
- Distinguish a confirmed root cause from a hypothesis; cite schema/data/handler evidence when claiming confirmation.
- Surface only scope-changing decisions, such as nullable relationship semantics, destructive retention policy, or real delivery transport versus an audited manual-send record.
- End with an explicit implementation gate when approval is required. The short chat response should contain the key root cause, decisions awaiting approval, verification status, and artifact link—not a duplicate of the full plan.

## Pitfalls

- Do not infer end-to-end completion from adjacent implementation.
- Do not classify an environment/setup failure as a product defect.
- Do not claim tests passed when only test source was inspected.
- Do not let frontend existence hide a mismatched or unregistered backend contract.
- Do not inflate percentages from file or route counts.
- Do not ask questions already answered by canonical repository documents.
- Audit-only means no formatting, generated report, migration, seed, build artifact, database, commit, or deployment changes unless separately authorized.
