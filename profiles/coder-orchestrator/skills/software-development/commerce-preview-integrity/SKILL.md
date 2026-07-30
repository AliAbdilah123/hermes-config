---
name: commerce-preview-integrity
description: Diagnose and verify data-backed commerce previews, including uploaded media, checkout, immutable policy provenance, cancellation compensation, and idempotent fulfillment.
---

# Commerce Preview Integrity

Use for isolated previews where products/packages, uploaded media, checkout, bookings, cancellation, compensation, or entitlements must behave like the real application without mutating production.

## Core workflow

1. Identify the exact preview worktree, API process, runtime database, public prefix, and asset route. Preserve dirty preview work.
2. Reproduce with the exact user, product/package, purchase, booking, and public route—not a nearby fixture.
3. Trace each value end to end: database → API DTO → frontend mapper → rendered public component.
4. Keep preview API, database, uploads, callbacks, and return URLs isolated.
5. Run focused regressions, broader relevant checks, a preview-scoped build, and exact public browser verification.
6. Report preview and production boundaries separately.

## Immutable policy provenance

For cancellation, expiry, or entitlement rules, resolve policy in this order:

1. immutable purchase-entry snapshot;
2. voucher's original package entry;
3. an explicitly documented legacy default.

Never evaluate an old purchase using the currently active package version. Distinguish a legacy `NULL` caused by pre-policy data or migration from an explicitly configured no-benefit rule.

When cancellation compensation looks wrong:

- inspect the exact claim, voucher, session, package-entry lineage, and snapshot;
- compute hours from the API clock and UTC session timestamp;
- add deterministic threshold tests with fixed timestamps;
- verify preview response and actual cancellation separately;
- assert the compensation voucher preserves product/package-entry lineage, expiry, and `origin_claim_id`;
- repeat cancellation to prove idempotency and no duplicate issuance.

## Nested-preview uploaded media

A successful form thumbnail is insufficient. Audit all public consumers: program product cards, package tabs/cards, product hero/detail, booking modal, and checkout summary.

API-hosted `/uploads/...` values must use the API-aware asset resolver, not the static Vite-base resolver. Nested previews also need an explicit `<preview>/uploads/` proxy to the isolated preview API; otherwise SPA fallback or production uploads can hide the defect.

Verify all of the following:

- API DTO contains the saved uploaded URL;
- preview-scoped image URL returns the real image MIME type;
- exact public route's rendered DOM contains the preview-scoped image URL;
- public HTML references preview-scoped hashed assets rather than production assets.

## Payment, booking-intent, and cancellation proof

For checkout, exercise authentication → quote → checkout → provider test confirmation → paid purchase → entitlement. Treat booking-origin checkout as a distinct contract: preserve `sessionId` and required custom-field answers, auto-book after payment, return `/my/bookings` with `booking_claim_id`, then focus the exact booking card. A direct package purchase must remain `/wallet` with no booking claim. Verify both Program Detail Upcoming Sessions and the full Sessions page use the shared flow.

For cancellation, exercise preview → cancellation → wallet compensation. Direct handler tests or HTTP 200 alone do not prove either flow.

See `references/booking-intent-media-cancellation.md` for the compact regression matrix covering booking redirects, nested-preview media, and legacy cancellation tiers.

## Product-type-dependent admin validation

Treat product type as a domain boundary, not merely a display choice. Scheduled/session products may require product managers, capacity, and weekly slots; simple products are not scheduled and must not inherit those requirements.

Enforce the rule symmetrically:

- frontend validation and helper text must require managers only for session products;
- create/edit payloads should send an empty manager list for simple products, avoiding stale hidden selections;
- backend create/edit validation must accept empty managers for simple products while rejecting them for session products;
- manager synchronization must accept an empty list and clear stale assignments;
- regressions should cover simple create/edit without managers and session create/edit rejection without managers.

Keep package-entry validation independent unless the product/package specification explicitly couples it to product type. A UI-only conditional is incomplete if the API still returns `manager_required`.

See `references/booking-intent-media-cancellation.md` for the commerce regression matrix and `references/product-type-validation.md` for the product-form boundary matrix.

## Pitfalls

- Do not infer readiness from the upload form preview.
- Do not treat `NULL` legacy policy as “no compensation” without proving that semantic.
- Do not use current mutable package settings for historical purchases.
- Do not claim E2E before the exact public route and downstream state are verified.
- Do not mutate production data to demonstrate preview behavior.
