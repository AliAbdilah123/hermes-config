# POS touch layouts and modal forms

Use this checklist for tablet/mobile point-of-sale screens with tap-to-add cards, long-press secondary actions, table selection, and line-item forms.

## Reproduce the reported viewport exactly

A high-resolution device screenshot may represent a smaller CSS viewport because of device-pixel ratio. Test the inferred CSS width and height, not only standard breakpoints. Pair screenshots with geometry assertions: no document overflow; catalog precedes ledger; cards fill tracks; text/actions do not overlap; fixed controls cover nothing.

A phone-only breakpoint can leave portrait tablets in a compressed desktop grid. Move the structural workspace transition to where its columns cease to be usable; do not patch individual card widths.

## Avoid duplicate checkout surfaces

If the ledger already contains totals and checkout, a floating mobile dock may duplicate actions and obscure products. Prefer removing the redundant dock over compensating padding when checkout remains readily reachable.

## Long-press menu details

- Long press opens details after a bounded delay.
- Pointer movement beyond a threshold and `pointercancel` cancel the timer.
- Suppress the click after a completed long press.
- Unavailable items stay focusable/detail-accessible while adding fails closed.
- Provide a discoverable keyboard equivalent such as `Shift+Enter` without an unwanted visible button.
- Never claim in the accessible label that an unavailable item can be added.

Test real pointer dispatch and keyboard activation publicly.

## Native multi-select for tables

Use `<select multiple>` when one order can occupy several tables. Include active, non-archived tables; show unavailable/non-enabled options disabled. Persist selected values exactly and verify held-order rehydration. Dine-in completion still requires at least one selection.

## Modalizing auxiliary forms

Use one shared accessible dialog and keep primary workflows, filters, and calculations inline. The dialog must move focus inside, trap Tab/Shift+Tab, close on Escape/backdrop, and restore focus. Keep validation inside and reset local state on cancel, close, and success.

For async receipt/OCR prefills, use a request-generation guard so stale completion cannot repopulate a closed form or overwrite a newer upload. Revoke object URLs and clear file/preview/error/parsing state through one reset path.

## Expandable line-item records

Disclosure buttons need `aria-expanded` and `aria-controls`; the panel needs a stable ID and labeled `role="region"`. Parent totals derive only from validated positive lines. Start with one line and prevent removal of the last line.
