# Active experiment session catalogs

Use this checklist for local/demo products where an admin-managed experiment temporarily replaces the catalog consumed during a user session.

## Domain invariants

- Clone the current versioned catalog into each experiment; do not let draft edits mutate the main catalog by reference.
- Keep explicit assumptions and per-item non-negative integer daily targets.
- Compute revenue as `target × draft current-version price`.
- Expand bundle targets through component quantities before aggregating recipe requirements.
- Aggregate ingredients by normalized name plus unit. Flag missing quantity or unit explicitly rather than silently presenting a precise purchasing total.
- Enforce the one-active invariant at the central state-update boundary, not only in the Activate button handler. This protects imports, migrations, and future callers.
- Resolve the session catalog in one shared selector: active experiment draft catalog, otherwise main catalog. Make every session consumer use that selector.
- Finalization requires confirmation, rejects an already-finalized experiment, records a timestamp, creates new main-catalog versions, and preserves old versions and historical sale snapshots.

## Focused regression matrix

1. Deterministic revenue from fixed prices and targets.
2. Bundle recipe expansion and ingredient aggregation.
3. Missing recipe quantity/unit labeling.
4. Activating B demotes active A atomically.
5. Session selector returns B's exact draft objects; with no active experiment it returns the main catalog.
6. Archive removes an experiment from active use.
7. First finalize increments current versions and preserves version history.
8. Second finalize fails without changing catalog state.
9. Existing order lines retain their sale-time names and prices.

## Verification order

Run focused pure-domain tests first, then UI/store persistence tests, typecheck, lint, full tests, and the production build. Run final tests after the last source edit so the completion evidence is fresh.
