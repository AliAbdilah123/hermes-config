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

## Verification

For targeted prototype refinements:

1. Build before deployment.
2. Use an OS-safe temporary script created with a `/tmp/hermes-verify-` prefix.
3. Assert the structural correction, scoped style change, and preservation of excluded breakpoint markup.
4. Remove the temporary script.
5. Report this as ad-hoc verification, not full-suite green.
6. Verify the public prototype route returns HTTP 200.

## Pitfalls

- Styling away a nested box while leaving unnecessary DOM hierarchy.
- Enlarging fonts globally and accidentally changing mobile.
- Treating a desktop deprecation as permission to redesign mobile.
- Claiming the entire suite passed when only focused source assertions ran.
- Implementing production changes from prototype feedback without explicit approval.

## References

- `references/detail-column-with-mobile-preservation.md` — concrete selected-session calendar pattern and verification checklist.
