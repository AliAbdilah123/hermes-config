# Opaque Job Inspector Visual Hierarchy

Use when a Radix/shadcn job detail or edit inspector looks transparent, visually messy, or like unrelated controls floating over the board.

## Root-cause checks

1. Inspect the active `DialogContent` variant and its class-merging order. Confirm the inspector class reaches the portalled element.
2. Check whether the panel relies only on a generic `bg-background` utility whose generated CSS/token is absent, overridden, or visually too close to the overlay/page.
3. Inspect the complete inspector rule for explicit background, border, shadow, padding, and scrolling—not just positioning.
4. Map visible content into semantic groups before changing layout: status metadata, task summary, editable definition, actions, timeline, and reply controls.

## Minimal fix

Prefer scoped CSS and a few semantic class seams over replacing the dialog component:

- Give the inspector an explicit opaque surface, border, and directional shadow.
- Reset heading/paragraph margins inside the inspector so inherited browser spacing does not create random gaps.
- Group task and editable-definition content into bordered section surfaces.
- Put peer actions in one flex row and style destructive actions distinctly.
- Preserve the existing Radix overlay, focus trap, close control, viewport anchoring, and mobile overflow rules.

## Regression check

Leave a lightweight source/CSS test asserting that the active inspector rule includes both its positioning reset and an explicit opaque background. Then run the native frontend tests/build, backend tests/build when assets are embedded, restart the service, and verify the deployed CSS hash and marker.

For visual-only changes, a screenshot of the authenticated inspector remains the final quality check when credentials/session access permit it; bundle markers prove deployment, not appearance.
