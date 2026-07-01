# Mobile discovery search/filter/card density corrections

Use when improving a mobile discovery/search results page with horizontal filter chips and card listings.

## Lessons from Komuna mobile discovery

- If the user says a proposed design still looks wrong and asks to “fix” it, implement the app change and verify the live page; do not only update the review/proposal artifact unless they explicitly ask for proposal-only work.
- Search should usually come before filters on mobile discovery pages: Search → primary filter rails → secondary filter rails → active chips → results.
- Avoid stacked mobile search forms. Use one cylindrical/pill search bar with:
  - input taking remaining width,
  - trailing circular/cylindrical icon submit button,
  - no leading decorative search icon when the action icon is on the right,
  - text hidden on mobile but preserved via `aria-label`/`title`.
- Filter chips can easily waste vertical space. For dense mobile rails, target roughly:
  - 32–34px min-height,
  - 6–7px vertical padding,
  - 10–11px horizontal padding,
  - 6px rail gap,
  - small label spacing and subtle dividers.
- Horizontal chip rails must actually scroll: `display:flex`, `flex-direction:row`, `overflow-x:auto`, `flex:0 0 auto` children, `scroll-snap-type:x proximity`, and `-webkit-overflow-scrolling:touch`. Do not rely on clipped/partial chips alone as the scroll affordance.
- Preserve theme tokens from the live page. For Komuna-style dark/warm UI, use existing paper/ink/accent variables and rounded forms instead of introducing a new black/white visual language.
- For oversized mobile program cards, prefer compact horizontal list cards over simply shrinking image-on-top cards when the goal is scan density. Aim for 2–3 visible results per viewport.

## Verification pattern

1. Build without stale Vite auth pollution when applicable: `env -u VITE_NEON_AUTH_URL node ./node_modules/vite/bin/vite.js build`.
2. Deploy/copy assets to the actual nginx-served path.
3. Verify public CSS/JS markers for the specific UI changes (e.g. `min-height:32px`, `border-radius:999px`, icon-button class names).
4. Capture a narrow mobile screenshot and visually confirm: search order, trailing icon button, smaller scrollable chips, and result density.
