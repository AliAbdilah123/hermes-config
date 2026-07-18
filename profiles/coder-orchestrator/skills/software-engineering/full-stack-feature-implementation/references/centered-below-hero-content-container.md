# Centering content below a full-width hero

Use this for small visual requests such as “indent the sections below the hero toward the middle” or “center the products area.”

## Minimal pattern

Keep the hero unchanged. Give each below-hero content section the same centered width constraint:

```css
.page-upcoming,
.page-catalog {
  box-sizing: border-box;
  width: min(100%, 1180px);
  margin-inline: auto;
}
```

Preserve existing section padding and mobile overrides. Reuse an existing project max-width token/value when one exists rather than introducing another width.

If the section background is intended to span edge-to-edge, put the max-width rule on an inner wrapper instead of the section itself. Otherwise, applying it directly to the section is the shortest valid change.

## Verification

1. Run the page’s focused component test.
2. Run the production build.
3. Deploy and confirm the public CSS contains the new max-width marker.
4. For visual-only changes, verify the live page at desktop and mobile widths when browser tooling is available.
5. Commit and push only after deployment verification.
