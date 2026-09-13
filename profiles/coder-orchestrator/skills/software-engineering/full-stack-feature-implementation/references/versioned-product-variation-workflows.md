# Versioned product variation workflows

Use this checklist when an existing commerce/POS application needs configurable free or paid choices before a product is added to a cart.

## Inspect before designing

Identify the exact paths for:

- Versioned product/catalog data, if present.
- Admin product creation and editing.
- Product-card click/add behavior.
- Cart reducer, line identity, totals, hold/restore, and checkout.
- Historical order snapshots and downstream operational views.
- Persistence/API migrations and legacy-record compatibility.
- Existing modal accessibility and responsive tests.

Do not assume a backend exists. If the product is intentionally local-storage backed, use its current persistence boundary rather than inventing an API.

## Minimal durable model

Prefer product-version-owned configuration and order-line-owned snapshots:

- A variation group has stable ID, label, required/optional policy, and options.
- An option has stable ID, label, and finite non-negative price delta.
- A cart/order line snapshots selected IDs, labels, deltas, base unit price, and final unit price.
- Existing final-line-price totals can remain unchanged if the configured-line constructor calculates the final unit price exactly once.
- New fields should be optional when legacy persisted records must remain readable.

For the first concrete workflow, stop at single-select groups unless multi-select/min-max behavior is explicitly required.

## Interaction invariants

- Configured product click opens customization before insertion.
- Unconfigured products retain direct add.
- Cancel adds nothing.
- Required groups block submission until selected.
- Optional groups expose an explicit None/Standard choice.
- Show Free for zero delta and a formatted surcharge otherwise.
- Show quantity and a live final add total.
- Preserve unavailable-product guards, long-press details, keyboard details, and pointer-cancel behavior.
- Reuse the existing accessible modal, native fieldsets/radios, focus trap, Escape handling, and focus restoration.

## Cart identity and history

Never merge lines by product ID alone after variations exist. Derive identity from the product/version plus a stable, sorted selection signature. Identical selections may merge; different selections must remain separate.

Do not re-price saved lines from the current product definition. Hold/resume, receipts, kitchen views, and order history must render the snapshotted labels and prices even after catalog edits.

## Ordered verification

1. Domain tests: validation, free/paid deltas, final unit price, line merging.
2. Admin tests: add/remove groups and options, validation, version creation, persistence.
3. Ordering tests: modal-before-add, required/optional behavior, cancel, quantity, direct add for plain products.
4. Lifecycle tests: discount/tax, hold/resume, completion, reload, later catalog edits, operational displays.
5. Accessibility/responsive checks: keyboard, focus, Escape, selected states, narrow viewport without overflow.
6. Fresh authenticated public E2E before declaring READY; include link, commit, and push evidence when implementation was requested.

## Scope ceiling

Defer reusable modifier libraries, nested groups, option inventory, ingredient consumption, and generalized selection-count engines until a real workflow requires them. Prefer the smallest extension of the existing product version, cart line, modal, and totals paths.
