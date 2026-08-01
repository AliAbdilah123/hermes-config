# Responsive Decorative Substitution Verification

Use when a complex visual component remains on desktop but is replaced by lightweight decoration on mobile.

## Implementation

- Keep the existing desktop component unchanged.
- Hide it only inside the intended mobile breakpoint.
- Prefer CSS-only ambient decoration when no interaction is needed.
- Add `prefers-reduced-motion: reduce` to stop motion while preserving a static decorative state.
- Keep decoration behind content and verify text contrast remains legible.

## Verification

1. Build with the exact public preview base path.
2. Mechanically assert the desktop rule remains and the mobile breakpoint hides the component.
3. Assert the animation keyframes and reduced-motion override exist.
4. Publish to the same preview for a follow-up revision rather than creating a new preview.
5. Inspect the deployed minified CSS semantically; minifiers may normalize values such as `transparent` to `0 0`.
6. Render the exact public route at desktop and mobile widths.
7. At mobile width, confirm the original component and controls are absent, the ambient decoration is visible but subtle, content remains legible, and no page/runtime error appears.
8. At desktop width, confirm the original component is still present.

A build and source assertion alone do not make the visual revision reviewable.