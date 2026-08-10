---
name: existing-product-workflow-module-planning
description: Plan a new intermediate workflow module inside an existing product by reconciling implemented architecture, domain boundaries, migration conflicts, UX, and phased delivery without changing product code.
version: 1.0.0
metadata:
  hermes:
    tags: [planning, product-architecture, workflow, migration, domain-modeling]
---

# Existing Product Workflow Module Planning

Use when a requested module sits between an existing source-of-truth entity and a downstream operational system, such as catalog → review → sales, intake → assessment → case, or Business → Prospect → Opportunity.

## Required approach

1. Verify the actual repository; placeholder or missing paths require candidate discovery and affiliation confirmation.
2. Inspect read-only across frontend routes/navigation/list/detail surfaces, backend routes/services, models, migrations, tenant/auth boundaries, current schema, and representative relationship counts.
3. Read existing product/architecture documents, but label documented targets separately from implemented behavior.
4. Identify every current entry point that bypasses the proposed workflow.
5. Define entity ownership before features:
   - canonical entity owns stable identity and shared facts;
   - intermediate entity owns research/review evidence, progress, decision, and pre-transition history;
   - downstream entity owns operational state after explicit acceptance.
6. Produce a conflict ledger: current behavior, conflict, smallest decision, and compatibility implication.
7. Prefer additive migration over a big-bang rewrite. Add the intermediate domain, link legacy downstream persistence where practical, centralize conversion transactionally, then retire old labels/fields later.
8. Define treatment of existing downstream records without fabricating missing historical evidence. Inspect representative counts grouped by legacy stage/status and source linkage; use that evidence to ask whether legacy records remain editable, become read-only, or are archived. Distinguish genuinely direct/legacy rows from valid source-linked rows that merely use old stage labels—do not archive both groups with one coarse predicate.
9. When a partial downstream module already exists, treat it as an implemented baseline—not a blank slate. Inspect its route shape, card/detail behavior, transition handler, persistence fields, and every direct-create/bulk-create bypass before proposing replacement work.
10. For drag/drop stage workflows, separate the gesture from the mutation: dropping proposes a destination, confirmation collects destination-specific required data, and only the validated server action changes stage. Always provide a keyboard/mobile non-drag alternative.
11. When the user resolves policy questions, propagate each answer into every affected plan section—not only a decisions appendix. Update state machines, schema/constraints, migration rules, API contracts, permissions, UX, notifications, tests, risks, and implementation tasks; remove stale alternatives and the resolved open-question list.
12. Re-render and verify both canonical source and public review artifact. Check exact decision phrases and confirm obsolete question headings are absent; use a cache-safe URL/version when an intermediary may serve stale HTML.
13. Publish the canonical plan plus the required styled review artifact, and include an explicit implementation gate.

## Mandatory plan sections

- Executive recommendation
- Current implementation baseline with exact file/symbol evidence
- Why the module is separate
- Entity ownership and state machines
- Architectural conflict ledger
- Navigation and page hierarchy
- Complete transition workflow and eligibility rules
- List/detail UX and all loading/empty/error/success states
- Reuse versus new component boundaries
- Evidence/checklist and explainable scoring rules
- Reports and immutable snapshot behavior
- Proposed data relationships, constraints, and API boundaries
- Legacy-record evidence and an explicit compatibility policy question
- Gesture-versus-mutation behavior for drag/drop, including confirmation, rollback, keyboard, and mobile paths
- MVP versus postponed scope
- Minimal-refactor migration phases
- Acceptance scenarios, risks, and decisions required
- Implementation gate

## Runtime/schema compatibility checks

When planning around a partially implemented downstream module, do not infer runtime readiness from source migrations alone:

- Read the live database's migration ledger and table schema in read-only mode, then compare them with every column/index the checked-out handlers query.
- Probe representative relationship counts separately (for example, downstream rows missing canonical, intermediate, or Offer links) before proposing legacy treatment.
- Distinguish a proven schema-version mismatch from the user's reported API symptom. A missing column can explain SQL failures, but it does not prove a generic `not_found` response came from that cause.
- Put exact authenticated request capture early in the plan: deployed revision, actual DB path, URL, method, status, role, and response. Classify routing, tenant-scoped absence, schema skew, relationship corruption, migration state, and frontend state separately.
- Sequence rollout as backup → grouped legacy counts → migration → integrity/foreign-key checks → authenticated list/detail smoke tests. Never use a repository-local database as proof of the deployed database's state.
- When a uniqueness constraint protects conversion, plan both an explicit transactional pre-check that returns the existing record ID for actionable UX and the database constraint as the race-safe backstop.

## Key pitfalls

- Never duplicate the canonical entity; reports are historical snapshots, not canonical copies.
- Do not let one status field represent lifecycle, qualification, outreach, and pipeline simultaneously.
- `not_checked` is not failure: it reduces completeness/confidence and may block finalization.
- In opportunity scoring, a failed quality check can increase service opportunity; expose signed rule contributions rather than assuming pass always scores higher.
- Automated audits may suggest evidence but must not silently mark checklist results or trigger conversion.
- Do not extend two competing detail-page implementations; name the canonical reuse target.
- Do not propose destructive table renames merely to fix terminology in the first release.
- When implementation changes are forbidden, create only new plan/review artifacts; describe schemas/endpoints as proposals, never as completed work.

## Supporting reference

See `references/intermediate-workflow-module-planning.md` for the detailed inspection, conflict, migration, scoring, and deliverable checklists.
