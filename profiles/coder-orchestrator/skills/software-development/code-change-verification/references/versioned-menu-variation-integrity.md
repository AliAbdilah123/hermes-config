# Versioned menu variation integrity

Use when a versioned catalog adds menu-specific choices/modifiers with free or paid price adjustments.

## Minimal model

- Keep variation groups/options on the immutable menu version.
- Snapshot selected group/option IDs, labels, deltas, base price, and final unit price into each cart/order line.
- Keep new fields optional when legacy saved lines must remain readable.
- Calculate discounts and tax from the snapshotted final line price, never by consulting the current catalog.

## Merge identity

Do not merge configured cart lines by only `menuId` plus group/option IDs. IDs commonly survive version edits while labels or prices change. Merge only when all sale-time values match: menu ID, snapshotted menu name, final unit price, and a canonical selection signature containing group ID/name, option ID/name, and price delta. Otherwise create a separate line.

## Authoring lifecycle

A configuration UI is incomplete if it only adds groups/options. Provide accessible removal controls for both, clone current choices into a new-version draft, validate trimmed case-insensitive unique names, require at least one option per retained group, and reject negative/non-finite deltas. Keep bundles/composites out unless their variation semantics are explicitly defined.

## Consumer surfaces

Render snapshot choices everywhere staff or users inspect the line—not only on summary cards. Verify cart, held/resumed order, Kitchen overview, opened Kitchen detail, completed order detail/history, and notes. Never resolve historical choice labels through the current menu.

## Focused regression matrix

1. Free and paid options compute the expected unit and quantity totals.
2. Required groups block submission; optional groups allow no selection.
3. Configured items open customization before add; plain items retain direct add.
4. Identical current snapshots may merge; same IDs with changed labels/base/delta/final price do not.
5. Admin can add and remove options/groups and save them as a new immutable version.
6. Hold/resume and completion preserve choices and prices after current-menu mutation.
7. Kitchen summary and full detail both show preparation-critical selections.
8. Public mobile E2E checks modal fit, focus/keyboard behavior, console/page/request failures, and exact live/cart totals.
