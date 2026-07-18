# Wallet voucher pocket animation and staged claim flow

Use when a Komuna wallet pocket has an approved physical voucher animation and a later feature adds session selection or booking.

## Preserve the approved object hierarchy

- The compact pocket card and the voucher modal are separate approved surfaces.
- The real voucher stack visible in the pocket is the source and return object.
- Opening pulls that stack out and leaves the pocket empty.
- The voucher modal must render real `.wallet-ticket` children; ticket drop/fan/return CSS cannot work if session cards replace those nodes.
- Closing reverses the same stack path. Never add fake return vouchers or allow the original stack to pop back after a gap.
- If the user says the animation is good, do not refactor or retime it while adding adjacent behavior.

## Correct staged interaction

When adding product-session selection, use:

1. **Pocket** — open with the approved literal stack animation.
2. **Voucher modal** — show voucher ID, product, status, expiry, source, perforation/stub, and inactive cut treatment.
3. **Voucher Claim** — only active, unexpired tickets proceed.
4. **Sessions modal** — fetch up to five upcoming sessions scoped by the voucher program and product; reuse the shared session card.
5. **Booking confirmation** — reuse the existing booking modal and claim API.

Do not fetch sessions merely by opening a pocket. Expired/claimed/refunded-only pockets remain inspectable without implying entitlement.

## Modal and Back semantics

- Mount exactly one `aria-modal` and one focus trap at a time.
- Booking cancel returns to the cached sessions list.
- Sessions Back returns to the stable open voucher modal without replaying the entrance animation.
- Voucher Put back runs the original full closing sequence.
- Each boundary needs Escape, translated labels, scroll lock, and focus restoration to its immediate trigger.
- In a shared modal shell, keep animation phase state separate from view state (`vouchers | sessions | booking`); ticket animation classes apply only to the voucher stage.

## Data correctness

- Fetch `status=upcoming`, selected `productId`, page 1, limit 5; defensively slice to five.
- Invalidate stale requests when sessions closes or the selected voucher changes.
- Keep subscription **Book** copy separate from voucher **Claim**.
- The claim API may select vouchers FIFO. Clicking a displayed ticket establishes product/session context unless the API explicitly accepts a voucher ID.
- Derive booking summary voucher and subscription access from real wallet data; never fabricate counts or hard-code subscription flags.

## Successful claim and animation snapshots

Refreshing wallet data can remove the consumed voucher—or the entire product group—before the 2880ms return sequence finishes. Snapshot the complete render context before refresh:

- active group identity/title;
- displayed voucher array;
- any data needed by the modal and focus/scroll lifecycle.

Render from this closing-group snapshot through the full close timer, not merely a voucher-array snapshot guarded by a live `activeGroup`. Clear the snapshot only when the original close sequence completes. This protects the last-visible-voucher case.

## Regression coverage

Use fake timers and cover:

- pocket open does not fetch sessions;
- active ticket Claim triggers the exact scoped request;
- inactive/cut tickets remain inspectable and cannot claim;
- ticket markup/design hooks restored from the known-good Git baseline rather than approximated;
- loading, empty, error/Retry, max five, and stale response;
- voucher → sessions → booking with one dialog;
- Back/cancel and focus restoration;
- exact phase milestones (including 650/1850/2320/2880ms where applicable);
- successful claim of the last visible voucher keeps the modal mounted through closing;
- real entitlement summary and subscription Book behavior.

## Verification gate

Focused tests and bundle/CSS markers prove wiring, not animation quality. Before claiming visual parity, exercise an authenticated wallet in a real browser and inspect/record open, Back, booking cancel/success, and Put back. If authentication is unavailable, report visual animation QA as unverified.
