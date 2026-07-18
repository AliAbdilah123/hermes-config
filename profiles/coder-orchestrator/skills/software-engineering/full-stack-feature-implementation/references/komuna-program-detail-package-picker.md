# Komuna Program Detail: No-Voucher Package Picker

Use when a Program Detail booking attempt has no eligible voucher and the modal should offer relevant packages directly.

## Minimal data path

Program Detail already loads program packages. Avoid a new endpoint when each package DTO includes `status`, `image_url`, `slug`, and entries with `product_id`, `product_name`, and `quantity`.

Filter client-side to:

- active packages only;
- packages where at least one entry's `product_id` matches the booked session product.

## Modal contract

- Show at most three matching packages initially; provide `Show all` / `Show less` when more exist.
- Use radio controls: exactly one package can be selected.
- Start with no package selected; do not initialize selection from the first matching package.
- Keep Continue disabled until an explicit user selection, and give the disabled state muted colors plus a `not-allowed` cursor so it is visually unambiguous.
- Continue to `/programs/:program/packages/:package/checkout`, preferring package slug with ID fallback.
- If no package matches, show an honest product-specific empty state; never offer unrelated packages.

## Package row content

Each option should show:

1. package image, with layout-safe fallback when absent;
2. package name as the entire header — do not synthesize or append `“N Sessions”`;
3. beneath it, the matching entry's product name and voucher quantity, e.g. `Sunrise Vinyasa · 4 vouchers`.

Use the matching package entry as the quantity source, not session counts or package-name parsing.

## Nearby Program Detail hierarchy

When membership is contextual rather than actionable, render small green copy immediately below category/open pills and above the program headline. Remove the redundant membership badge from the CTA row.

Give Book controls a dedicated hover/focus class so their lift/scale/shadow differs from the clickable session-card hover. Preserve `prefers-reduced-motion` behavior and existing click propagation boundaries.

## TDD checks

- only active matching packages appear;
- first three visible, expansion and collapse work;
- package image, exact package name, product name, and voucher quantity render;
- only one radio remains selected;
- initial state has no checked radio and Continue is disabled;
- selecting a package checks only that radio, enables Continue, and preserves the canonical slug/ID fallback checkout URL;
- no-match state;
- membership copy and DOM order;
- card click navigates while Book click invokes booking without card navigation.

## Deployment verification

Build Komuna with `VITE_NEON_AUTH_URL` absent, deploy, then verify exact production markers from source. Read the implemented empty-state/toggle copy before writing bundle assertions; do not guess marker text. Confirm local email sign-in remains present and deprecated Neon markers remain absent.
