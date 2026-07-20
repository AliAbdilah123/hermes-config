# Evidence-Backed Improvement Audit

## Audit Tracks

### Security and architecture

Check trust boundaries first:

- tenant/account ownership on every list, read, insert, update, delete, and parent-child operation;
- uniqueness and foreign-key constraints aligned with tenancy;
- bootstrap credentials, fallback secrets, cookies, CORS, webhook authenticity, and internal worker authentication;
- HTTP timeouts, header/body limits, strict decoding, filesystem errors, and persistence errors;
- migrations, rollback, and historical-schema verification;
- queued work, retries, idempotency, atomic state transitions, and terminal failure states.

### Product and operations

Trace visible promises to real behavior:

- navigation entries that are actually rendered;
- filters and CTAs connected to predicates/endpoints;
- scheduled features with a real scheduler;
- bulk operations preserving the full selection and reporting per-item outcomes;
- optimistic UI rollback on failure;
- empty/error states that do not silently substitute demo data;
- external actions marked complete only after verified completion;
- data completeness, provenance, confidence, freshness, validation, and deduplication;
- deployment, backup, restore, health checks, CI, logging, and rollback documentation.

## Ranking

- Critical: confidentiality, authorization, known credentials/secrets, destructive cross-account behavior.
- High: misleading success, broken core workflows, unrecoverable outreach/state changes.
- Medium: migrations, data quality, runtime hardening, test gaps, reporting depth.
- Low: copy consistency, visual polish, internal terminology.

## Report Pattern

For every finding include:

1. Short outcome-focused title.
2. What is confirmed and why it matters.
3. Exact file/line evidence.
4. Minimum practical next action.

End with a phased sequence:

1. Stop the risk.
2. Restore operational truth.
3. Improve data and delivery leverage.

Keep the report decision-oriented. Do not dump every observation or repeat the same root cause across many cards.