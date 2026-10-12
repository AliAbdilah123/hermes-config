# Repeated create forms

Use this pattern when a creation dialog must save several records consecutively without closing.

## Minimal implementation

1. Keep the existing validated submit path as the single source of truth.
2. Add a second submit button (for example, **Create & add another**) with a distinct submitter value. Do not duplicate creation logic.
3. After a successful create:
   - normal submit: close the dialog;
   - repeated-create submit: clear all native fields and React-managed nested state, clear errors, restore creation defaults, and keep the dialog open.
4. Force a fresh form instance when uncontrolled inputs use `defaultValue`. Calling `form.reset()` alone may leave React's uncontrolled-input baseline stale; rotate the form's React `key` after the successful repeated-create submission.
5. Keep edit mode unchanged unless repeated editing is explicitly requested.

## Verification

Start with a failing interaction test. Create record A with the repeated-create action, then record B with the normal action. Verify:

- the dialog remains open after A and closes after B;
- persistence requests contain independent records (`A`, then `B`), with no concatenated/stale values;
- nested state such as ingredients, components, variations, files, and errors does not leak.

When persistence is queued or optimistic, wait for each outbound write before entering the next record and assert request snapshots rather than reading storage immediately. Server reconciliation can temporarily replace optimistic UI state, making DOM or local-storage assertions race-prone even when submitted payloads are correct.

## Pitfalls

- `form.reset()` does not reset separately controlled React state.
- Reusing the same keyed form can yield values such as `FirstSecond` under automation because the uncontrolled input did not truly remount.
- Submitting B before A's queued write completes can test queue timing instead of repeated-create behavior.
- Do not expand a small repeated-entry request into CSV import, editable grids, or batch APIs unless requested.