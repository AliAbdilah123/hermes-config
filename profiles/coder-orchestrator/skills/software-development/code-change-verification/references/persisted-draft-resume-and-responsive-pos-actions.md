# Persisted draft/resume and responsive POS action verification

Use this when adding held, open, draft, or resumable records to an order/form workflow.

## Round-trip fidelity

- Save through the real UI, resume through the real UI, and assert every editable field survives: top-level name, mode, selected table/resource, line quantities, modifiers, notes, discounts, and other draft state.
- Restore persisted line snapshots directly. Reconstructing from the current catalog can silently drop modifiers/notes, change historical prices, omit unavailable/deleted products, or merge intentionally distinct lines.
- Assert unpaid drafts have no payment field/event and are excluded from completed revenue. Check persisted status, audit wording, and payment absence independently.
- Restore the complete editing context, not only lines: service/order type, resource/table IDs (including a tested legacy singular-field migration), and any discount/coupon identity.
- Resolve saved discounts by stable persisted identity or normalized code. If the referenced discount is missing or inactive, preserve the saved line snapshots, do not silently apply a different discount, recalculate from the restored editable state, and show an explicit warning.
- Make every resumable record reachable. A single “resume first draft” control is insufficient when several held/open records may coexist.
- Disable resume while a non-empty draft is active unless an explicit merge/replace confirmation exists. A cancelled replacement must leave both the active cart and held record unchanged.
- Validate the persisted payload before mutating current state. Remove/transition the held record only after restoration is accepted and all synchronous restoration preconditions pass; malformed records must remain recoverable.
- Add focused RED→GREEN regressions for: full customized round-trip (including modifier and note), cancelled replacement, unavailable discount handling, and legacy resource restoration. Plain-item resume tests do not detect lossy reconstruction.

## Responsive action additions

Adding header icons, fields, or footer actions can create intrinsic overflow that `overflow-x: clip` merely conceals.

At each narrow target:

1. Assert `document.documentElement.scrollWidth === innerWidth`.
2. Measure header, workspace, and action-container right edges and require each to be within `innerWidth`.
3. Scroll to document bottom and require the new terminal action’s bounds to be inside the viewport.
4. For fixed cart docks, verify enough document-bottom clearance exists for underlying actions.
5. Use viewport screenshots for fixed controls. Full-page screenshot stitching can falsely depict overlap.

Prefer the smallest responsive correction: remove/hide a secondary control at the narrow breakpoint, use `minmax(0,1fr)`, and place secondary actions in a compact row with the primary action full-width. Do not redesign the workflow merely to solve width pressure.

## Product-card control collisions

When an absolutely positioned add/action button overlaps a price or label in a narrow card, padding the text is not automatically a valid fix: it can leave too little width for localized currency and cause clipping. Resolve the collision structurally when the card has an unused region—for example, move the action into the top-right icon row and restore full-width price text at the bottom.

Verify at the narrowest tablet/desktop card width, not only mobile and wide desktop:

1. Capture the breakpoint where sidebars and ledgers squeeze the product canvas most.
2. Require the complete localized currency string to remain visible and not intersect the action control.
3. Re-run the public workflow and viewport matrix after moving the control because a new absolute anchor can affect touch hierarchy.

## Focused TDD locator validity

A RED test is valid only when it reaches the intended missing behavior. If it fails earlier because a semantic locator is ambiguous or uses the wrong accessible name, repair the test locator and rerun RED. For product-card and current-line controls with similar names, scope to the relevant container or use the complete accessible name. Do not implement against a harness failure.
