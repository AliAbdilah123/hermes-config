# Holistic PRD Revision Checklist

Use when stakeholders provide product decisions against an existing PRD and explicitly do not want an appended change log.

## Integration pass

Rewrite affected claims across the whole artifact rather than adding a “revisions” section. Reconcile each decision against:

- product vision, ICP, value proposition, and scope boundary;
- registration, verification, workspace setup, onboarding, FTUE, and daily-return flow;
- canonical entities, state machines, invariants, permissions, and audit history;
- information architecture, navigation order, page purpose, and empty/error states;
- dashboard hierarchy, action ranking, personalization, and historical analytics;
- database relationships, versioning, provenance, events, and reporting semantics;
- roadmap, MVP exclusions, phase outcomes, and cross-phase definition of done.

## Product critique prompts

Do not accept stakeholder wording literally when it creates poor UX or architecture. In particular, test whether:

- mandatory onboarding collects only information needed for first value;
- workspace-level setup is incorrectly repeated for invited users;
- long-cycle milestones improperly gate access or dashboard usefulness;
- “personalization” implies hardcoded one-off widgets instead of configuration-driven capabilities;
- current-state fields would erase historical reporting or auditability;
- AI-readiness is turning into speculative AI infrastructure;
- phases deliver isolated modules rather than a complete user outcome.

State each materially improved decision visibly, with the rationale and simpler alternative.

## Practical architecture defaults

- Separate canonical records from workflow views.
- Keep qualification specific to an Offer and preserve rule/evidence versions.
- Model due work consistently so the dashboard can be an action queue rather than a collection of bespoke widgets.
- Preserve stage transitions and closed outcomes as history; closing a deal should not delete or freeze the underlying account.
- Prefer stable IDs, provenance, domain events, and an outbox as future intelligence seams. Defer embeddings, vector stores, prompt registries, and model gateways until a validated use case requires them.

## Verification

After the final rewrite, deterministically assert that every requested topic appears, all internal anchors and relative links resolve, responsive/accessibility hooks remain, and the public artifact matches the committed source. A public HTTP 200 alone is insufficient.
