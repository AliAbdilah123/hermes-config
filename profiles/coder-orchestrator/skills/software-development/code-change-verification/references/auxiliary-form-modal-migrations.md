# Auxiliary form → modal migrations

Use this checklist when moving a group of inline create/edit forms into dialogs without changing domain behavior.

## Inventory and conversion

1. Search every named auxiliary route for inline `<form>`, prompt-based edits, and existing modal usage. Treat create and edit as separate entry paths.
2. Reuse the application's existing accessible `Modal` and `FormActions`; do not add another dialog abstraction.
3. Put the trigger in the existing `PageHead` or `SectionTitle` action slot. Keep only registry/policy/read-only content in page flow.
4. Preserve the original submit handler and validation. Validation errors stay inside the open modal.
5. On success: persist, reset transient form state, clear errors, and close. On cancel/backdrop close: do not mutate persisted data; clear stale errors and disposable draft state.
6. For edit flows, open with current values prefilled. Replace `prompt()` edits with the same modal form contract.
7. For complex controlled forms, reset all related arrays/mode state on close (for example ingredients, components, and item kind), not just the record ID.

## Test migration

Follow RED→GREEN with one representative form first, then apply the established pattern.

- Before opening, assert the form control is absent.
- Click the page/section trigger and assert the named dialog appears.
- Perform existing validation and successful-submit assertions through the dialog.
- When trigger and submit share the same accessible name (for example both are “Add table”), scope the submit query to the dialog: `within(screen.getByRole('dialog', {name: 'Add table'})).getByRole('button', {name: 'Add table'})`.
- Update old workflow tests to open the modal before querying fields. A missing label after conversion is usually stale test setup, not a product defect.
- Cover at least one cancel-without-mutation path and one prefilled edit path across the migration set.

## Completion gate

Run focused modal tests first, then the complete canonical test suite, lint, typecheck, build, and `git diff --check`. Modal conversions often break unrelated established workflows only because those tests assumed forms were always mounted.
