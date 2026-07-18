# Mobile Discovery Program Rails

Use when an approved mobile discovery layout keeps vertical desktop-style cards but presents them in horizontal category rails.

## Minimal implementation pattern

1. Reuse the existing card component; add only a narrow rail wrapper. If a grid component owns the wrapper, support a `contentsOnly` option rather than duplicating card mapping.
2. Keep desktop as the existing grid. Under the mobile breakpoint, make the rail track `display:flex`, `overflow-x:auto`, and `scroll-snap-type:x mandatory`; give cards a fixed responsive basis such as `min(72vw, 220px)` and `scroll-snap-align:start`.
3. Append a real link card (`View all programs`) as the final flex item. Keep the section-header View All link on desktop and hide it on mobile.
4. Derive directional controls from actual geometry:
   - back available when `scrollLeft > epsilon`
   - forward available when `scrollLeft < scrollWidth - clientWidth - epsilon`
   - update on scroll and resize
   - start: forward only; middle: both; end: back only; no overflow: neither
5. Scroll one card width plus gap per chevron activation. Use native smooth scrolling, but respect reduced-motion preferences.
6. Hide the browser scrollbar and expose a small theme-token-based interaction indicator. Show it on scroll/focus/keyboard interaction, reset a short idle timer, then fade it. Do not leave a default scrollbar permanently visible.
7. Use existing theme variables for surfaces, borders, ink, accent, focus rings, and shadows so dark/light modes require no parallel hard-coded palette.
8. Keep the track keyboard-focusable and give chevrons localized accessible labels. Preserve at least 32–44px usable targets and visible focus states.

## TDD boundary

Before implementation, add a page-level test proving:
- each populated merchandising section renders a focusable rail;
- previous/next controls exist with accessible labels;
- the terminal View All link points to the canonical search page.

JSDOM has no real layout, so geometry-controlled buttons may remain `hidden`. Assert their DOM presence via selectors or test geometry logic separately; do not weaken production visibility rules to satisfy JSDOM.

## Verification

- Run the focused Discovery test and production build first.
- Verify deployed index asset hashes changed and public JS/CSS contain rail-specific markers.
- Capture a narrow-viewport screenshot when possible.
- If the broad repository suite has unrelated failures, report focused tests/build as passing and list broad-suite debt separately; do not expand a scoped visual task into unrelated repairs.

## Pitfalls

- Do not replace familiar vertical cards with elongated horizontal cards unless explicitly approved.
- Do not show both chevrons permanently; controls must reflect remaining content.
- Do not use arbitrary colors for light/dark variants.
- Do not use a native default-looking permanent scrollbar.
- A pseudo-element on an overflowing track can move with scroll content. Prefer an indicator owned by the non-scrolling wrapper when it must remain viewport-fixed or represent true scroll position.
