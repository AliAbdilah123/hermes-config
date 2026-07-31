# Deployment target and booking-flow proof

Use when a fix exists in a preview branch but the user reports production behavior, especially checkout or booking redirects.

## Establish the real target first

1. Repeat the exact URL/environment being reported: preview or production.
2. Inspect that environment's served HTML and hashed bundle, not merely the source worktree.
3. Compare deployed branch ancestry with the fix commit. A pushed preview branch is not evidence that production contains the fix.
4. If production has equivalent or squashed code but not the original SHA, compare behavior and files rather than concluding it is absent.
5. Never repair an unrelated preview mount and present that as resolution of a production report.

## Booking redirect matrix

Prove all four cases through the user-facing browser flow:

| Entry | Entitlement | Expected behavior |
|---|---|---|
| Program Upcoming Sessions | eligible voucher/subscription | confirmation + required custom fields -> claim -> My Bookings focused on claim |
| Full Sessions page | eligible voucher/subscription | same algorithm and destination |
| Either session surface | no eligible entitlement | package choice -> checkout with session intent -> paid auto-book -> My Bookings focused on claim |
| Package card/literal checkout | no session intent | paid purchase -> Wallet |

## Required production evidence

- Use an authenticated browser account whose voucher/product/session relationship is known.
- Capture voucher summary and verify the session product ID matches an active, unexpired voucher or active subscription.
- Capture the claim request/response for voucher-backed booking, including custom-field answers and returned claim ID.
- Observe final browser route, navigation state, and focused/highlighted booking card.
- For checkout-origin booking, capture checkout intent, payment confirmation, `booking_status`, `booking_claim_id`, and final route.
- Separately test direct package purchase remains Wallet-bound.

Source strings, unit tests, build success, HTTP 200, and `/my/bookings` appearing in a minified bundle are supporting evidence only—not production E2E proof.

## Deployment collision check

Before blaming code regression, verify the reported URL still maps to the intended artifact and API: web-server location, filesystem directory, runtime basename/API base, and served hash. If another deployment removed a preview mount, restore it—but keep that incident distinct from a production bug report.
