# Async review and cross-layer release gates

Use when implementation/review work is delegated in the background and the change spans persistence, API filtering, and UI affordances.

## Review completion is a hard gate

A background review that has not returned is **pending evidence**, not optional feedback.

Before claiming completion, committing, pushing, or deploying:

1. List every delegated verification/review task dispatched for the change.
2. Wait for all blocking reviewers to return.
3. Read the complete review output, including any truncated continuation file.
4. Resolve every high/medium finding or explicitly document why it is not applicable.
5. Re-run fresh tests after the final fixes.
6. Only then commit, deploy, and report READY.

Do not let passing tests or a successful deploy override a still-pending independent review. If review arrives after release and finds a real defect, immediately correct the completion claim, fix via TDD, redeploy, and provide the superseding commit.

## Cross-layer checklist

### Schema-derived indexes and metadata

When adding derived tables such as tags, search indexes, aggregates, or junction rows:

- Verify new writes populate them.
- Verify updates delete/recompute stale derived rows transactionally.
- Verify **existing records are backfilled** during migration or a one-time post-migration hook.
- Add a migration regression test that starts with pre-feature data, reapplies/open-migrates, and asserts the derived rows exist.
- Verify the migration ledger records the backfill and production data contains expected rows after deploy.

Creating tables without backfilling historical records produces a feature that only works for newly edited data.

### Repeated query parameters

For multi-select filters serialized as repeated parameters:

- Validate allowed values.
- Bound the number of values before constructing SQL placeholders.
- Bound individual value length and reject empty malformed values.
- Deduplicate when useful.
- Test oversized counts and oversized values return a bounded `400`, not a SQLite variable-limit error or `500`.

Parameterized SQL prevents injection but does not prevent resource-exhaustion or placeholder-limit failures.

### Actionable UI affordances

Only show an action when the backing operation can do meaningful work.

For example, a “Load post” button should be gated by a supported source and resolvable attachment/reference—not merely by the presence of any HTTP URL. Add tests for:

- supported source + supported attachment;
- manual note containing an ordinary URL;
- supported source with unsupported/missing reference;
- retry/error behavior.

A button that succeeds without changing the UI is a correctness defect, even if it does not throw.

## Release evidence

After fixes, require all of:

- focused regression tests;
- full backend/frontend tests and type/build checks;
- migration applied against the actual runtime database;
- authenticated public API probe for validation boundaries;
- deployed asset/DOM evidence for UI controls;
- local HEAD equals pushed remote HEAD.
