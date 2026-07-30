# Booking intent, nested media, and cancellation regressions

## Booking-origin checkout versus direct purchase

Redirect and downstream behavior derive from intent, not merely from voucher issuance.

- **Booking origin, eligible voucher/subscription:** collect required custom fields, create claim, then navigate to `/my/bookings` with the claim ID.
- **Booking origin, no eligible voucher:** select a matching package, carry `sessionId` plus custom-field answers through checkout, provider confirmation, and auto-booking; return `/my/bookings` with `booking_claim_id`.
- **Direct package-card/literal checkout:** omit `sessionId`, issue entitlements only, and return `/wallet` without a booking claim.
- Program Detail Upcoming Sessions and the full Sessions page should share one booking modal/intent builder. Do not maintain route-specific redirects.
- Payment return should pass claim ID as navigation state. My Bookings should wait for data, then scroll to, focus, and visibly highlight the exact card.

Verify publicly with two fresh preview users: booking checkout must report `booking_status=booked`, `/my/bookings`, and non-empty `booking_claim_id`; direct checkout must report `booking_status=not_requested`, `/wallet`, and no claim.

## Nested-preview uploaded media

Stored `/uploads/...` URLs need the API-aware resolver in every public consumer, including product cards/heroes, package cards, and booking package pickers. For a relative API base `/previews/<slug>/api/v1`, resolve media beneath `/previews/<slug>/uploads/...` and proxy that prefix to the isolated API before SPA fallback.

Verify real product and package uploads return image MIME types and appear in the rendered exact public route. Form-preview success is not public-view proof.

## Legacy cancellation tiers

Policy order is purchase snapshot → original package entry → documented legacy default. A `NULL` tier on an old session-package entry may mean “predates configurable tiers,” not “no compensation.” Scope any fallback to the legacy session-voucher case; keep simple-product and subscription semantics separate.

For a reported booking, trace user → membership → claim → voucher → package entry/snapshot → session start. Test fixed timestamps around thresholds, preview and cancellation responses, compensation lineage/expiry, and repeated cancellation idempotency.