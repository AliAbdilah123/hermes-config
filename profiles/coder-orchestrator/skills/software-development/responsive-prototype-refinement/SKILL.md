---
name: responsive-prototype-refinement
description: Refine approved or review-stage responsive UI prototypes after user feedback while preserving explicitly excluded breakpoints and removing redundant visual nesting.
version: 1.0.0
---

# Responsive Prototype Refinement

## Use when

Use this skill when a user reviews an interactive or static UI prototype and asks for targeted hierarchy, typography, spacing, or breakpoint-specific corrections before production implementation.

## Workflow

1. Re-read the latest user correction and identify the exact surface and breakpoint in scope.
2. Inspect the component hierarchy before changing CSS. If the complaint is “box inside box,” determine which wrapper owns layout and which wrapper is only decorative.
3. Remove the redundant decorative wrapper rather than hiding its border or layering compensating CSS.
4. Move the content to the requested structural level, preserving semantics, state, labels, and actions.
5. Scope typography and spacing changes beneath the affected desktop/mobile container. Do not use broad selectors when another breakpoint is explicitly excluded.
6. Preserve out-of-scope breakpoint markup and interaction literally unless a shared dependency makes a minimal change unavoidable.
7. Exercise the changed interaction, build the artifact, publish it, and verify the public route.

## Hierarchy rule: column, not card-in-column

When a grid column already has panel/card treatment, selected-item content should usually be direct children of that column. Do not add another bordered, rounded panel inside it merely to group details. Use spacing, typography, and lightweight separators for grouping. Remove the redundant wrapper in the component tree; do not merely neutralize its CSS.

## Typography after flattening

Compact card typography often looks undersized after content is promoted to a full column. Rebalance the hierarchy at the scoped container level:

- make the selected item title clearly dominant;
- enlarge date/facts and section headings proportionally;
- retain readable labels and metadata;
- avoid globally changing shared component typography.

## Fixed-height workspace footer visibility

When a control is present in the DOM but reported missing on laptop-height viewports, do not assume placement order proves visibility. Inspect the entire height-containment chain first:

- fixed shells such as `height: 100dvh` and `overflow: hidden`;
- grid/flex ancestors missing `min-height: 0`;
- which child owns scrolling;
- footer/composer rows that can be pushed beyond the clipped workspace.

Prefer one bounded workspace where only the timeline/content row scrolls and the composer plus adjacent actions remain non-scrolling rows. Keep tightly related controls in one footer wrapper when attachment summaries or validation messages can add rows. Verify both viewport width and height at representative laptop dimensions; width-only responsive checks miss this failure class.

For actions that create a resource asynchronously and must open it in a new tab, calling `window.open` only after `await` may be blocked because the browser no longer considers it part of the user gesture. Prefer reserving a blank tab synchronously from the submit gesture, then set its location after creation succeeds and close it on failure. If that interaction cannot reserve a tab safely, provide a visible ordinary anchor to the created resource as fallback. Always use `noopener`/`noreferrer` semantics and keep the originating tab unchanged when requested.

## Settings-tab consolidation

When feedback renames a settings tab and moves existing controls into it:

- treat the new tab name as a broader information-architecture boundary, not a label-only change;
- move the existing control implementations rather than recreating them, preserving persistence hooks, accessibility labels, and state;
- remove the controls from their old tab and mechanically verify there is exactly one rendered instance of each;
- keep unrelated account/security actions in their original tab;
- preserve internal section IDs and legacy routes when that avoids needless compatibility churn, unless the user explicitly requests URL changes;
- update visible labels and headings in every supported locale;
- test through normal tab navigation, then change each moved preference and verify persistence plus independence after reload.

For language, display currency, and theme controls, verify all three coexist in Preferences; changing one must not reset either of the others. Display currency must remain presentation-only.

## Breakpoint preservation

“Do not change mobile” means:

- keep mobile markup and interaction intact;
- scope new rules under the desktop container;
- do not infer that removing a desktop feature authorizes removing its mobile counterpart;
- compare source/diff for mobile selectors and components before completion.

Desktop and mobile may intentionally use different interaction models during prototype review.

## Proportional hero-height refinements

When the user asks to reduce an image-led hero by a percentage, first identify what actually determines its rendered height. If the image uses `width: 100%` plus `aspect-ratio`, change the ratio rather than adding fixed heights or JavaScript. For example, changing a portrait ratio from `4 / 5` to `8 / 5` halves the rendered height at the same width. Scope the override to the requested page and preserve any existing mobile ratio unless mobile was explicitly included.

Do not confuse source-level proportional math with visual approval. Verify the ratio and breakpoint preservation mechanically, then provide the exact public route for user approval when approval is the done definition.

## Data-backed compact cards

When replacing compact card metadata (price, status, badges) with API-provided descriptions:

- inspect whether the description contract permits rich-text HTML before rendering it as ordinary React text;
- reuse the codebase's existing rich-text-to-plain-text helper at the card boundary rather than displaying raw tags or introducing a second sanitizer;
- clamp the normalized plain text, not the raw HTML string, so markup does not consume the visible line budget;
- preserve the remaining hierarchy (for example category and location) unless explicitly removed;
- test with a rich-text fixture, then visually inspect exact public desktop and mobile cards because plain-text fixtures will not expose raw-markup rendering.

See `references/compact-cards-with-rich-text-descriptions.md` for the focused implementation and verification pattern.

## Comprehensive multi-surface responsive audits

When the request spans several related product surfaces rather than one visual correction, begin with a read-only route/component map before proposing CSS changes. Reconcile the user's page names with actual routing and state boundaries: a requested “Contact page” may be a Business-detail drawer, while Assessment or Report may be tabs rather than standalone routes. Record these distinctions so implementation does not invent duplicate pages or test the wrong surface.

Use supplied screenshots as concrete regression evidence, but trace the symptom through the shell and breakpoint rules before assigning a fix. In particular, distinguish desktop sidebar collapse state from mobile drawer-open state; stale shared state across breakpoint changes can leave a wide drawer covering narrow content even when individual pages are responsive. Inspect global overflow suppression such as `overflow: hidden`, because it can conceal the owning component rather than eliminate overflow.

For a comprehensive audit plan:

1. Map every requested experience to its exact route/state, primary component, shared shell, and style owner.
2. Compare implementation breakpoints and behavior with the repository's own UI specification; call out contradictions explicitly.
3. Establish a named viewport matrix covering desktop, compact desktop/tablet landscape, tablet portrait, the reported failing viewport, mobile, and desktop→mobile→desktop resizing.
4. Fix in dependency order: shell/navigation first; then feature-owned tables, maps, forms, drawers, modals, timelines, Kanban, and menus; then shared touch/accessibility standards; finally browser regression coverage.
5. Keep genuinely wide surfaces locally scrollable while asserting that the document itself never overflows horizontally.
6. Preserve critical actions at narrow widths; wrap, stack, or consolidate them rather than hiding them.
7. Treat drag-and-drop as enhancement: retain an explicit keyboard/touch operation such as a Move control.
8. Run existing unit/type/API checks read-only to register the baseline separately from future browser E2E.
9. For complex work that requires planning before implementation, publish the reviewable plan first and make the implementation gate explicit; do not imply code was changed.

For a concise reusable checklist and suggested browser assertions, see `references/comprehensive-responsive-audit.md`.

## Verification

For targeted prototype refinements:

1. Once the visual change is ready for review (and always before committing), build the artifact.
2. Even when the normal build passes, also create and run an OS-safe focused temporary script with `mktemp /tmp/hermes-verify-<topic>-XXXXXX`; use a cleanup trap so it cannot remain in the workspace.
3. Assert the exact changed behavior: new scoped selectors/values or structure are present, superseded values are absent, and excluded breakpoints remain unchanged when relevant.
4. Run the focused script before claiming completion; do not assume a passing compiler or production bundle proves a visual spacing rule.
5. Report the focused result explicitly as “ad-hoc targeted verification passed,” not full-suite green. Report the build separately if it also passed.
6. Verify the exact public prototype route returns HTTP 200; a homepage probe is not evidence for a nested detail route.
7. If user approval is the done definition, report the implementation as awaiting approval even after mechanical checks pass.

For interactive image prototypes, visible controls and source-string checks are not enough. Exercise the complete state cycle: open preview without launching the picker, edit from the current saved preview, pan/zoom, save and reopen, delete into a usable empty state, replace via supported input methods, cancel back to the last saved state, and close only from preview. Use a same-origin sample image when Canvas export is involved; remote hotlinks can taint Canvas. Temporary `localStorage` persistence should store a bounded crop (for example 512×512), never the original upload. When a user reports “no change,” verify the exact cache-busted public URL and visible behavior before explaining the implementation.

## Single-column commerce refinements

When a checkout or purchase page changes from two columns to one, size the centered parent once and let both cards use `width: 100%`. This guarantees matching edges without duplicated width values. Place package details first and payment/order details below; reassess sticky positioning because a formerly side-mounted payment card usually no longer needs it. When approval is the done definition, demonstrate this in an isolated non-transactional preview before changing production behavior. See `references/centered-single-column-checkout.md`.

## Conversational localization refinement

When prototype feedback says a locale sounds rigid or translated too literally, audit the whole locale catalog rather than replacing only the cited headline. Preserve keys, interpolation tokens, plurals, markup, and established domain terms; validate the catalog mechanically, then render representative surfaces in the selected locale. For Indonesian casual-polite copy, avoid `Anda`, prefer direct active phrasing, use `kamu` only when needed, and add conversational particles sparingly. A rejected lexical choice such as `Temukan` should be removed consistently from user-facing discovery copy, but do not blindly replace semantically distinct browse/filter actions. See `references/conversational-localization-refinement.md` for the editing and verification checklist.

## Staggered exit-animation continuity

When elements briefly disappear after an action and then reappear when their staggered exit animation starts, inspect the animation fill mode before changing React state, visibility, or timing. A delayed animation with `forwards` applies neither the first nor final keyframe during its delay, so the element falls back to its underlying style and may vanish or jump. If the first keyframe represents the required pre-animation pose, use `both` (or `backwards` when the final pose must not persist) so that first keyframe applies throughout the delay.

Keep this as a minimal CSS correction when the DOM remains mounted correctly. Add a focused style-contract regression asserting the exact selector uses the intended fill mode, then exercise the complete interaction because source assertions cannot prove visual continuity. For an existing reviewed preview, rebuild and republish the same preview route rather than creating a replacement preview.

## Rejected-delta rollback

When the user asks to revert a reviewed component, undo only the latest rejected delta on that component; preserve all previously accepted preview changes. Restore the component and its focused tests together, rerun the focused test and preview-path build, then republish and visually verify the exact surface.

If an old assertion fails because the established locale/formatter emits an equivalent value (for example `IDR 28` rather than `$28`), update the stale assertion instead of changing the restored UI merely to satisfy literal test text.

Scope visual QA to the exact DOM surface. Removing an `Open` badge from each card does not imply removing a page-level “Open to Join” section. Name the relevant element/class in screenshot-review prompts so similarly worded headings do not become false failures.

## Optional product/package selection refinements

For session-detail forms that combine owned optional products with fallback package checkout, keep owned-product state and package-checkout state mutually exclusive, default both to explicit **None**, and verify persistence through canonical refetch and edit rehydration—not only the outbound save payload. Direct package **Buy** and **Checkout and save** require distinct return intentions.

When cards expose wallet inventory, put each product's count at the trailing edge and treat selection as a **prospective** reduction: selecting an item shows `activeCount - 1`, switching items restores the prior product, and selecting **None** restores every count. Clamp at zero. The preview must not claim/consume a voucher; assert disclosure save makes no checkout or provider call. Use a three-column card grid (`radio | wrapping copy | right-aligned count`) and stack the count label compactly on narrow screens so long names cannot collide with inventory.

Keep ordinary bookable-session test fixtures safely in the future while preserving their intended weekday and timezone semantics. Fixed near-future dates eventually become “past,” silently disabling booking controls and causing misleading failures. Keep a separate explicit historical fixture for past-session behavior.

See `references/session-detail-simple-product-package-picker.md` for the full state, payment-return, remaining-voucher count, responsive layout, persistence, visual-border, and verification matrix.

## Pitfalls

- Letting hidden or stale package selection keep the main action checkout-oriented after an owned product is selected.
- Resetting an API-persisted optional product to **None** when reopening edit mode, causing a later save to erase it.
- Treating a pale parent-card border around a flush placeholder as part of the placeholder asset instead of inspecting hierarchy first.
- Reverting the whole preview when only the latest component delta was rejected.
- Changing restored UI to satisfy a stale locale-specific literal assertion.
- Letting screenshot QA confuse a page-level heading with the exact card-level element under review.
- Independently sizing vertically stacked cards instead of giving them one shared centered parent.
- Leaving side-column sticky behavior on a payment card after moving it below package details.
- Styling away a nested box while leaving unnecessary DOM hierarchy.
- Enlarging fonts globally and accidentally changing mobile.
- Treating a desktop deprecation as permission to redesign mobile.
- Claiming the entire suite passed when only focused source assertions ran.
- Implementing production changes from prototype feedback without explicit approval.

## References

- `references/detail-column-with-mobile-preservation.md` — concrete selected-session calendar pattern and verification checklist.
- `references/session-detail-simple-product-package-picker.md` — checkout-consistent vertical Simple product selection, capped horizontal package recommendations, empty states, and focused verification matrix.
