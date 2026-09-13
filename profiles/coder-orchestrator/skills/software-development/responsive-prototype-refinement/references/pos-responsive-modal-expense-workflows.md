# Responsive POS, modal forms, and line-item expenses

Use this checklist when refining a touch-first POS after screenshot feedback.

## Diagnose responsive order-entry failures

- Reproduce the screenshot’s **CSS viewport**, not its physical pixel dimensions; Android tablet screenshots often represent roughly half the image width in CSS pixels.
- Measure the actual card, catalog, ledger, and workspace rectangles. A grid can technically fit while product cards remain unusably narrow.
- At intermediate/tablet widths, stop using a compressed three-column desktop workspace once the product canvas cannot provide practical card widths. Stack `categories → products → ledger` before cards collapse.
- Keep the catalog before the empty ledger on narrow/tablet layouts so the primary selling action appears first.
- Avoid fixed/min-height table selectors and empty ledgers that consume the viewport.
- A fixed mobile checkout dock must not duplicate or cover the ledger checkout. If the ledger remains fully accessible, deletion of the redundant dock is safer than compensating offsets.
- Verify: no document overflow, products appear within the initial viewport, card content/actions do not overlap, and the last content can scroll clear.

## Long-press menu details

- Keep ordinary tap/Enter/Space as the primary add action for sellable items.
- Start a bounded pointer timer (about 600 ms); cancel it on pointer movement beyond a small threshold, pointer cancel, or pointer up.
- Suppress the post-long-press click so opening details does not also add the item.
- Do not add a visible Details button when long press is the requested interaction.
- Preserve a discoverable keyboard equivalent on the card itself (for example Shift+Enter), described in `aria-label`/`title`.
- Sold-out items should remain focusable/detail-accessible while add is guarded; use `aria-disabled`, not native `disabled`, when details must still be reachable. Ensure the accessible label does not claim unavailable items can be added.

## Table multi-select

- A native `<select multiple>` is the minimum robust control when multiple tables can be attached.
- Render active, non-archived tables as options; keep unavailable/non-enabled tables visible but disabled.
- Derive selected IDs from `selectedOptions` and persist the exact array.
- Verify held-order rehydration, multiple selections, disabled unavailable options, and table-required checkout validation.

## Auxiliary forms as modals

- Modalize create/edit workflows, not filters, calculations, small settings, checkout, or the main New Order workflow.
- Keep all fields and submit actions in one `<form>`; fields outside the form break Enter submission and native required validation.
- A shared modal must move focus inside, trap Tab/Shift+Tab, close on Escape, restore launcher focus, and retain backdrop close.
- Keep validation in the dialog; Cancel must not mutate data; success resets and closes.

## Line-item expenses

- Expense parent amount is derived exclusively from line items; do not expose an editable parent amount.
- Initialize exactly one line and prevent removal of the final line.
- Require at least one valid positive line before save.
- Receipt parsing prefills editable draft fields and never auto-saves.
- One reset path must handle X, backdrop, Cancel, and success: clear form, lines, errors, file/input, preview, and parsing state; revoke object URLs.
- Guard asynchronous receipt responses with a request generation/token so a closed dialog or newer upload cannot be overwritten by stale completion.
- Expense rows should disclose line details inline with `aria-expanded`, `aria-controls`, a stable panel ID, and a labelled `role="region"`.
- Do not retain dead prompt-based Edit controls for line-backed expenses. Either implement full modal editing or omit Edit.

## Verification

1. Focused interaction tests for long press cancellation, keyboard details, sold-out guard, table selection, modal keyboard behavior, expense reset/stale OCR, and disclosure linkage.
2. Full tests, lint, typecheck, production subpath build, and diff check.
3. Deploy the exact asset and verify its hash in public HTML.
4. Public browser checks at the reported tablet viewport and a representative phone viewport.
5. Capture and visually inspect fresh screenshots; DOM geometry and HTTP 200 are not visual proof.
