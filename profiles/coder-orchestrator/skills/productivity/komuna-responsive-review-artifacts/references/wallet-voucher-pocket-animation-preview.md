# Wallet voucher pocket animation preview handoff

Use this reference when a Komuna review artifact previews a nuanced UI animation that will later be implemented in the live React app.

## User-approved behavior from voucher pocket session

- The preview should use the real wallet/pocket visual components as closely as possible, not an abstract mock.
- Once the user approves an animation, preserve its timing/easing/feel exactly; subsequent changes should be narrowly scoped (e.g. copy text or glow intensity only).
- The voucher pocket animation must be literal:
  - On open, the visible vouchers already in the pocket are the ones pulled upward/outward.
  - The wallet card/pocket must allow overflow during the pull, so vouchers can travel above the card boundary toward the top of the screen.
  - While voucher details are shown in the modal, the pocket stack is empty/hidden.
  - On close, the put-back animation should be the open animation in reverse using the pocket's own voucher stack, not a separate fake return component.
  - Avoid a gap where the pocket is empty and then the original stack pops back in after the return animation.
- If the user says an animation is good, do not refactor or retime it during implementation; port the exact approved keyframe values/class-state sequencing.

## Implementation pattern used

- Add modal phase classes to the real pocket button, e.g. `wallet-pocket-button--opening`, `wallet-pocket-button--open`, `wallet-pocket-button--closing`, plus `wallet-pocket-button--empty`.
- Store each pocket voucher's home transform in a CSS variable (e.g. `--wallet-pocket-home`) so keyframes can animate from/to the real stacked positions.
- Use opening keyframe on `.wallet-pocket-button--opening .wallet-pocket-voucher`.
- Use reverse/put-back keyframe on `.wallet-pocket-button--closing .wallet-pocket-voucher` with the same stagger as the approved preview.
- Remove separate floating/fake voucher return layers when the requirement is literal return to pocket.
- Keep close/reset timers long enough for the last staggered voucher to finish before removing closing/empty classes.

## Verification

- Build the web app (`npm run build`) after TypeScript/CSS changes.
- Deploy Komuna public root to `/var/www/html/projects/komuna/` and verify the public HTML references the new hashed asset.
- Verify the public CSS asset contains the new keyframe/class names with a cache-busting query string.
