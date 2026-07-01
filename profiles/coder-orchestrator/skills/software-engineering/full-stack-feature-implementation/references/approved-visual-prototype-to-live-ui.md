# Approved visual prototype → live UI implementation

Use when the user has already approved a visual/animation prototype and asks to apply it to a live React/Vite app.

## Workflow

1. Re-open the live component and CSS before editing; prototypes often have different markup from production.
2. Port the approved visual state with the smallest production seam:
   - conditional class names in the component;
   - CSS-only motion/effects when possible;
   - no new dependency for clip-path, shakes, staggered drops, hover highlights, or fly-in/out sprites.
3. Preserve unaffected states explicitly. Example: active vouchers stay normal; only claimed/expired/refunded/inactive vouchers get the cut/torn treatment.
4. For physical ticket/voucher cut effects:
   - split the main body and stub with a small gap;
   - hide the original perforation line on cut vouchers;
   - use full-element `clip-path: polygon(...)` shapes that include rectangle corners, not only the jagged edge, or the voucher content may disappear;
   - add the dashed/perforation texture as pseudo-elements on both torn edges;
   - optionally rotate/offset the stub and add a muted USED/CLAIMED stamp.
5. For pocket/modal animations:
   - keep modal state as an explicit phase (`opening`, `open`, `closing`) so close animations can complete before unmounting;
   - do not reveal the modal too early: source/pocket fly-out sprites should finish or nearly finish before backdrop/panel fade-in and before modal tickets drop;
   - close sequentially: modal tickets reverse the entrance with comparable stagger, rotation, overshoot, and upward exit first; then panel/backdrop fade; then wallet-page sprites fly back to the pocket;
   - capture the clicked pocket's `getBoundingClientRect()` to target return sprites;
   - lock `document.body.style.overflow = 'hidden'` while the modal is mounted and restore the previous value on cleanup, so the page behind cannot scroll;
   - put hover transitions on the base card state, not only `:hover`, so unhover is smooth.
6. Add a focused test for the production wiring: opening adds animation phase classes, inactive modal vouchers get the cut class, active vouchers do not, close switches to closing phase.
7. Verify with the project-native focused test and production build.
8. Deploy and verify the public index asset hashes plus deployed CSS/JS bundle markers for the new classes/copy. For Vite SPAs, bundle markers are more reliable than looking for app text in `index.html`.

## Pitfalls

- Do not implement the animation prototype before the user-approved ordering if they say “apply the cut effect first, then animation.”
- Avoid unmounting the modal immediately on close; that causes blank/no visible reverse animation.
- Do not animate return-to-pocket sprites behind the fading modal layer; give them a higher z-index during the return stage.
- In repos with broad pre-existing uncommitted work, stage only the files you intentionally changed. If a shared CSS file already contains unrelated changes, inspect the scoped diff carefully before committing.
