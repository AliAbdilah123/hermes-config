# Reusable feature-slice audits

Use when auditing multiple repositories for implemented capabilities that could become reusable `feature-*` skills.

## Required report shape

For every assigned repository, report:

- canonical purpose
- implemented reusable feature slices only
- exact source paths and important functions
- frontend, backend, schema/migration, environment-variable **names**, and tests
- pitfalls supported by source or git history
- proposed class-level `feature-*` skill and concrete template/reference/script candidates
- fresh verification result, separating pre-existing baseline failures from audit-induced failures

Classify alternate worktrees, task branches, forks, and predecessor checkouts as lineage evidence rather than independent repositories when they share a canonical codebase.

## Workflow

1. Establish repository identity and lineage. Inspect root, remote, branch, common Git directory/worktree list, HEAD, and recent history. Choose one canonical repository; label other checkouts as provenance or regression evidence.
2. Inventory high-signal surfaces: README, manifests, source, migrations/schema, tests, examples, deployment, and environment examples. Exclude dependencies, generated bundles, caches, databases, and binaries.
3. Find vertical slices, not nouns. Require evidence across at least two layers, such as handler plus schema, worker plus tests, or UI plus API. UI labels and README claims alone are insufficient.
4. Trace exact seams. Record paths, functions/types, routes, tables/constraints, frontend components, env names, and focused tests. Never print environment values or credentials.
5. Consult existing feature skills before proposing names. Treat them as coverage boundaries; cite existing coverage and propose only the uncovered capability.
6. Run focused native tests where practical and report results per surface. Run backend tests, frontend tests, and builds as independent commands when their outcomes matter; a long `&&` chain lets an early failure hide later evidence. In a read-only audit, fresh failures are baseline unless the audit changed tracked source.
   - If repository-wide discovery is blocked by an unreadable/generated directory, run the owning package tests and report both the narrower pass and broader blocker.
   - If a failed test file was already modified at initial status, label the result as dirty-worktree baseline rather than attributing it to canonical HEAD.
   - Distinguish a missing test script/harness from a failing test suite.
7. Use history as evidence only when paired with current code where possible. History can establish recurring persistence, migration, route-drift, or portability pitfalls.
8. Rank extraction readiness. Strong candidates have a complete contract, schema, implementation, and focused tests. Qualify mock-only providers, stubs, stale schemas, external symlinks, empty initialization shells, and broken baseline suites.

## Skill-design rules

- Prefer class-level umbrellas such as developer-platform OAuth, durable messaging, media caching, or asynchronous document ingestion.
- Put repository-specific provenance, paths, and failure history in `references/`, not the umbrella SKILL.md.
- Candidate templates should be copyable seams: migrations, provider interfaces, workers, route contracts, UI primitives, and focused regression tests.
- Do not extract broad application glue unchanged.
- Do not create a skill from one helper unless another repository corroborates the pattern.

## Pitfalls

- Treating each checkout as an independent repository inflates findings and duplicates proposals.
- Reporting broad features without exact functions makes extraction unverifiable.
- Secret values are unnecessary; names and semantics suffice.
- A passing backend does not erase a failing frontend baseline.
- A mocked provider call or fixed-cost stub is not a production-ready integration.
- Runtime `ALTER TABLE`, duplicate migration IDs, external symlinks, and stale architecture docs are extraction risks.
