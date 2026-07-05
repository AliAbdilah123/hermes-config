# Compact dashboard card visual fixes

Use when a dashboard card looks loose/empty after shadcn/legacy card retrofits, especially in a CSS grid row where neighboring cards make the row taller.

## Pattern

1. Patch the card itself before changing data/component structure:
   - `align-self:start` on the specific grid card to stop visual stretching.
   - Reduce only that card's `CardHeader`/`CardContent` padding with a scoped selector.
   - Tighten the title line-height/font-size and row `min-height`/padding.
2. Tighten dense list rows with CSS-only constraints:
   - smaller icon dimensions,
   - nowrap/ellipsis on secondary chips for desktop,
   - compact badge padding/font-size,
   - smaller action buttons.
3. Keep responsive escape hatches:
   - allow chips to wrap again at tablet/mobile widths,
   - stack row metadata/actions under the name on narrow viewports.
4. Verify the real deployed CSS asset, not just the build:
   - run the production build,
   - deploy/copy `dist/`,
   - curl the public `index.html` and confirm new hashed JS/CSS assets,
   - curl the deployed CSS and grep for a unique marker such as `align-self:start`.

## Pitfall

If a screenshot shows a single compact row floating inside a large white card, the bug may be grid/card stretching rather than row content. Try `align-self:start` on the affected card before adding wrappers, JS, or slicing list length.