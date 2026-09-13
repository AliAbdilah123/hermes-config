# Compact POS form and expense corrections

Use this recipe when an existing POS-like SPA needs focused responsive layout, modal-form, and line-item ledger corrections without redesigning desktop behavior.

## Test-first acceptance

Write boundary tests before editing production code and confirm they fail for the missing behavior:

- Creation fields are absent before the page-level action is activated.
- Activating the action opens a named `dialog`.
- Successful submit persists data, resets state, closes the dialog, and leaves the new record visible.
- A line-item form starts with exactly one line and disables removal of that final line.
- The parent amount field is absent when amount is derived from required child lines.
- A ledger record with children starts collapsed, expands to show description, quantity/unit, and amount, then collapses again.

When moving existing inline forms into dialogs, update older tests to activate the dialog before querying its fields. This is an intentional contract change, not a reason to leave hidden or duplicated controls in the page.

## Minimal implementation pattern

- Reuse the application's existing modal and form-action primitives.
- Keep validation errors inside the dialog so error context remains adjacent to the form.
- Close only after successful persistence; cancellation must not save.
- Initialize required line collections with one blank line.
- Prevent the final line's removal both in the button state and state updater.
- Derive the record total solely from cleaned positive line amounts; do not retain a competing parent amount input.
- For OCR/import results with zero lines, restore one blank editable line. Imported values prefill only and never auto-save.
- Keep expanded-row state to one optional record ID unless multi-expand behavior is explicitly required.

## Responsive CSS checks

At the named mobile/tablet breakpoints:

- Scope overrides to the page/workspace root.
- Make the workspace a single-column grid in semantic order: categories, products, ledger.
- Use `minmax(0, 1fr)`/`min-width: 0` where grid or flex children can force horizontal overflow.
- Let product cards fill their grid tracks; integrate secondary detail controls into the card stack rather than absolutely positioning them outside narrow cards.
- Reduce inherited desktop minimum heights for the mobile ledger instead of hiding it.
- Preserve desktop selectors and verify page-level `scrollWidth <= clientWidth` with live geometry when browser QA is available.

## Verification

Run the focused interaction test first, then the complete test suite, lint, typecheck, production build, and `git diff --check`. Report each boundary separately and do not claim visual proof unless a real viewport/geometry check was performed.
