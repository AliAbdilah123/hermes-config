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

## Pitfalls

- Independently sizing vertically stacked cards instead of giving them one shared centered parent.
- Leaving side-column sticky behavior on a payment card after moving it below package details.
- Styling away a nested box while leaving unnecessary DOM hierarchy.
- Enlarging fonts globally and accidentally changing mobile.
- Treating a desktop deprecation as permission to redesign mobile.
- Claiming the entire suite passed when only focused source assertions ran.
- Implementing production changes from prototype feedback without explicit approval.

## References

- `references/detail-column-with-mobile-preservation.md` — concrete selected-session calendar pattern and verification checklist.
