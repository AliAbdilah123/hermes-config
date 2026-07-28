# Post-purchase wallet voucher arrival

Use when Komuna should visually acknowledge vouchers issued by a completed package purchase.

## Trust boundary

Treat router state and query parameters only as hints containing a purchase ID. Before showing any paid-success banner or animation, call the existing owner-scoped confirmation endpoint and require a server-verified `paid` result. Never let client-provided `vouchers_issued` establish payment or fulfillment. Wallet must never create or retry checkout; it only presents benefits issued by the canonical payment-finalization path.

## Exact fulfillment matching

1. Confirm the purchase server-side.
2. Fetch the wallet.
3. Select vouchers whose `purchase_id` exactly matches the confirmed purchase.
4. Require the matched count to equal the server-confirmed `vouchers_issued` count.
5. If wallet visibility may lag fulfillment, retry with a short bounded backoff—not immediate back-to-back reads.
6. If retries are exhausted, retain the purchase hint so refresh can retry later. Never claim an incorrect quantity.
7. For zero-voucher or subscription-only purchases, do not show a voucher-added banner.
8. Keep `pending` confirmations replayable until a terminal result is known.

## One-time experience

- Preserve the purchase hint while confirmation, bounded retries, or animation are in progress so refresh/navigation can safely replay an interrupted experience.
- Acknowledge and clear it only after the animation completes, the user dismisses it, or a truthful terminal non-voucher result is reached.
- Ordinary wallet visits and acknowledged purchases must not replay it.
- Never show the experience for pending, failed, expired, refunded, mismatched, unauthorized, or client-forged purchases.

## UX contract

- Show a top confirmation banner with accessible collapse/expand and dismiss controls.
- Animate only newly issued vouchers into their matching product pocket.
- For a product with no previous pocket, render the new pocket empty first, animate the vouchers into it, then reveal its normal filled state.
- Keep existing pockets stable.
- Make the entire pocket a native keyboard-accessible control; do not add a redundant `Open pocket` text action or nest controls inside the pocket button.
- Use transform/opacity motion only and honor `prefers-reduced-motion`; reduced motion preserves truthful final state without spatial travel.
- Keep pocket rows aligned and responsive using existing design tokens, equal card heights, `minmax(0, 1fr)` tracks, and appropriate 4/3/2/1-column wrapping.
- Motion should explain where benefits went; avoid unrelated confetti or celebration.

## Preview fixtures

A fake hosted-checkout URL that merely resembles Xendit is misleading and must never be attached to a visible `Complete payment` action. To review pending-payment UI, either:

- use a genuine Xendit test-mode invoice created through the normal checkout path; or
- render a non-clickable fixture clearly labeled as display-only.

Clean up preview-only purchase rows after review. Do not alter production data or provider checkout behavior. If a real test invoice is created, clean it up through a provider-supported operation when available; do not guess provider endpoint paths.

## TDD coverage

Write failing tests first for:

- forged router state and unauthorized/unpaid purchases;
- verified paid purchase with exact multi-voucher count and pocket matching;
- zero-voucher/subscription-only purchase;
- delayed wallet visibility succeeding inside bounded retries;
- exhausted mismatch and pending confirmation remaining replayable;
- new empty pocket transitioning to filled;
- refresh before completion versus refresh after acknowledgment;
- collapse, expand, dismiss, keyboard activation, and reduced motion;
- absence of redundant `Open pocket` text.

## Verification

Run changed-file lint, focused Wallet/payment-return/checkout tests, and a production build. Browser-verify the exact isolated preview route/state, public JS/CSS MIME types, updated semantic bundle markers, and that production still serves its prior artifact. Do not infer visual behavior from HTTP 200 or bundle presence alone.
