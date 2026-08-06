# Session-detail Simple product and package selection

Use this pattern when a session-detail disclosure lets an attendant optionally attach an owned Simple product or buy a package when no eligible owned voucher exists.

## State and UI contract

- Simple product is optional. Always render an explicit **None** radio and default to it for a new edit.
- Render eligible owned Simple products as a vertical radio list.
- If the member has eligible owned products, package recommendations must not control the main action. Selecting an owned product or **None** clears every stale package/checkout intent.
- Owned-product selection uses **Save details** and must call disclosure persistence only—never create checkout or navigate to the payment provider.
- When no eligible owned product exists, still show **None**, then show up to three active packages containing a `simple` product voucher entry. Preserve API order and exclude archived, session-only, unrelated, and subscription-only entries.
- Reuse the established checkout package-card design. Render recommendations horizontally; use horizontal scrolling/snap on narrow screens. Render naturally when only one or two exist.
- Package selection defaults to **None** and can be reset to **None**.
- Put **Buy** beside the package price. Direct **Buy** may start checkout immediately while preserving the edit draft and an explicit return intent.
- If a package is selected through the form, the main action becomes **Checkout and save**. Keep direct-buy return intent (restore draft/edit mode without saving) distinct from checkout-and-save return intent (save after confirmed payment).
- After direct-buy payment return, restore the same route, edit mode, unchanged draft, and newly purchased Simple product selection. Keep return handling preview-aware and idempotent.
- If there are no eligible packages, keep the section visible with the exact agreed empty-state copy rather than hiding it.

## Persistence round-trip rule

Do not stop at asserting the outbound payload. Verify the complete boundary:

1. selected radio state;
2. frontend request payload;
3. API decode/validation;
4. database write;
5. detail-query DTO;
6. canonical refetch;
7. reopening edit mode hydrates the persisted selection;
8. a second save retains it.

A common regression is `beginEdit()` resetting the selected product to `None` even though the API correctly persisted and returned its ID. Hydrate from the saved `merchandise_product_id` only when it remains among eligible owned products; otherwise safely fall back to **None**. Confirm attaching metadata does not claim or consume the owned voucher.

## Visual hierarchy pitfall

When a placeholder image sits flush against a card edge, a pale border on the parent card can look like an unintended white frame around the image. Inspect the parent border before changing the placeholder asset or gradient. If the border is redundant, remove only that declaration and preserve clipping, radius, background, and shadow; verify the exact selector mechanically and obtain visual approval.

## Focused verification matrix

Cover independently:

1. Owned products exist: **None** defaults selected; choosing a product yields **Save details**, no checkout request, and survives refetch/reopen/resave.
2. Choosing **None** clears the saved product and stale package intent.
3. No owned products: **None** remains visible and package selection defaults to none.
4. Package selection can be cancelled; main action toggles exactly between **Save details** and **Checkout and save**.
5. Direct **Buy** preserves draft and returns in edit mode without auto-save; checkout-and-save retains its save-after-payment behavior.
6. Zero, one, two, and more-than-three package states; mixed ineligible entries excluded.
7. Desktop and narrow viewport horizontal layout.
8. Parent-card border removal does not alter radius, overflow clipping, background, or shadow.

Build with the exact preview base, publish to the existing isolated preview route, and verify the public rendered state. Payment-provider E2E and authenticated save/reload E2E remain pending unless actually exercised on the public preview.