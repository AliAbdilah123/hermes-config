# Carousel theme, motion, and live-visibility fixes

Use this checklist when a carousel feels visually bland, flashes or glows in dark mode, uses off-brand type, or changes slides abruptly.

## Implementation

- Reuse the site's existing `--font-sans`, `--font-serif`, and `--font-mono` tokens rather than introducing an isolated font stack.
- Use theme surface, ink, rule, and accent variables for captions, controls, and dots. Avoid hard-coded white overlays and borders: they commonly become glowing blocks in dark mode.
- Keep outgoing and incoming slides mounted together during directional motion. Assign explicit entering/exiting classes for next and previous navigation; hiding the prior slide immediately makes CSS motion impossible.
- Apply the same transition path to autoplay, arrows, and dot navigation.
- Make inactive slides unfocusable and `aria-hidden`; respect `prefers-reduced-motion` by disabling animation and hiding outgoing content.

## Focused checks

- Assert next and previous actions produce the expected entering and exiting direction classes.
- Assert only the active slide is keyboard-focusable and exposed to assistive technology.
- Run the focused carousel tests and production build after the final edit.

## Live visibility

A passing test and build do not show that a visual fix reached the user. For an already-deployed SPA:

1. Deploy the final generated assets to the actual web root.
2. Fetch public HTML and confirm it references the newly generated asset hashes.
3. Verify the public route returns successfully.
4. If the user says they see no difference, inspect the live served asset and page before changing code again; stale deployment or caching can mimic an ineffective implementation.
5. When the user explicitly says to redo the work directly, do not delegate the retry.
