# Member disclosure and entitlement editing

Use for owner-editable booking/session disclosures that include custom fields and optional simple-product metadata.

## Boundaries

- Answers and selected simple products belong only in the booking owner's attendant disclosure.
- Never leak them into operator participant lists.
- Preserve the separate Admin attendance UI.
- Treat simple-product selection as metadata unless redemption/consumption is explicitly requested.

## Eligibility

Do not offer every active simple product in a program. Choices must come from the current member's active, unexpired voucher/subscription entitlements under existing domain rules. Enforce the same rule server-side.

An already-saved product that later becomes expired, archived, or ineligible remains readable and clearable, but cannot be selected again.

When there are zero eligible choices, show at most three active packages containing simple-product entries, in existing API order. Exclude session-only packages and do not invent ranking. Reuse the booking modal's package cards, quote display, and checkout handoff.

## Edit contract

- Owner-only mutation, scoped through claim → member → user and program/session.
- Cancelled, past, or completed claims are read-only.
- Load current field definitions plus saved answers.
- Preserve stale removed-field answers as read-only history; submit only current field IDs.
- Validate required fields at both UI and API boundaries.
- Replace answers and selection atomically and append an audit event.
- UI supports Read → Edit → Cancel/Save, prevents duplicate submit, exposes errors, manages focus, and refetches canonical state after save.

## Verification

Exercise authenticated public E2E for both cases:

1. entitled member edits an answer, chooses/clears a product, saves, editor closes, canonical values render, and persistence matches;
2. unentitled member sees only matching simple-product packages, capped at three without Show All.

Also verify mobile overflow/sticky controls and assert participant DOM contains no disclosure values. Restore mutated preview fixtures through the same owner API afterward.
