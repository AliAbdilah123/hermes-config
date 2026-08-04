# Intermediate Workflow Module Planning Reference

## Read-only baseline inspection

1. Inspect the actual frontend route/page state, navigation labels, list/detail surfaces, and every entry point into the downstream workflow.
2. Inspect backend routes, handlers/services, tenant/auth boundaries, DTOs, migrations, constraints, and live schema in read-only mode.
3. Inspect representative row counts and relationships read-only; an existing table does not prove the feature is operational.
4. Read product documents, but distinguish target architecture from implemented behavior.
5. Cite exact files and symbols as baseline evidence.

## Conflict checklist

Look for:

- status fields mixing lifecycle, qualification, outreach, and pipeline;
- labels using the proposed entity name for legacy records;
- direct downstream creation that bypasses review;
- legacy persistence names that differ from actual domain roles;
- universal scores where scoring should be contextual;
- duplicate detail implementations;
- activity history that begins only after conversion;
- SPA routing that lacks durable detail URLs;
- automated enrichment presented as verified evidence.

## Minimal-refactor sequence

1. Add intermediate entity and evidence/history tables.
2. Preserve canonical identity.
3. Add compatibility links to current downstream persistence.
4. Create one explicit transactional conversion operation.
5. Route all creation entry points through that operation.
6. Stop new writes to legacy review fields while temporarily preserving reads.
7. Rename misleading UI labels at workflow rollout.
8. Defer destructive table renames, unified activity migrations, and column removal.
9. Grandfather legacy downstream records without inventing reviews.

## Explainable scoring checklist

- Store result, note, evidence source, reviewer, and timestamp per check.
- Keep `not_checked` separate from fail.
- Record contextual pass/fail impacts and weights.
- Snapshot ruleset version and signed item contribution.
- Expose calculated versus manually overridden result.
- Preserve prior calculations.
- Require manual confirmation for downstream transition.
- Treat automation as suggested evidence only.

## Review artifact checklist

- Canonical markdown/source exists.
- Styled HTML review page exists with persistent light/dark mode.
- Long documents include a table of contents.
- Proposed schemas/APIs are labeled as future implementation scope.
- Existing PRDs are untouched when the user prohibits PRD changes.
- Local/public HTTP and exact content markers are verified.
- Final response states the implementation gate and ends with the review URL.
