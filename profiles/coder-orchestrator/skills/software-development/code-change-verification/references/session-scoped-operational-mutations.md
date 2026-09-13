# Session-scoped operational mutations

Use when an operational UI mutates records resolved through a session selector, such as a kitchen changing menu availability while an active experiment temporarily supplies the session catalog.

## Mutation contract

- Read and write through the same session resolution rule. If reads resolve `active experiment catalog → main catalog`, mutations must update the active experiment draft when present and the main catalog otherwise.
- Match by stable record ID; do not mutate the derived selector output or clone blindly into both sources.
- Preserve immutable version/history arrays when changing operational state such as `available`, `low`, or `sold-out`.
- Apply status transitions conditionally at the central update boundary (for example, only `Preparing → Ready`) so stale/repeated actions cannot advance a newer state.
- Keep least-privileged role routes explicit and verify that route-derived role synchronization cannot promote the role.

## Focused regression matrix

1. With no active override, mutation persists to the main record and survives reload.
2. With an active override, mutation persists only to its draft record; the main record and version history remain unchanged.
3. Every consumer using the session selector reflects the mutation immediately (for POS, low remains sellable and sold-out is disabled).
4. Restoring the default state works from each non-default state.
5. A stale transition against a non-source status is a no-op.
6. The operational role lacks unrelated checkout, administration, and reporting controls.

## Compatibility pitfall

When strengthening visible status copy, preserve established accessible-name contracts where practical. Put legacy/general wording before the new specific detail (for example, `Unavailable · Sold out`) or update all affected regressions deliberately; inserting a new word between previously adjacent matcher terms can break otherwise valid accessibility tests.
