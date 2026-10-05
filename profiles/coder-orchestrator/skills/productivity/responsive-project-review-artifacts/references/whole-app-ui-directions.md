# Whole-app UI direction comparisons

Use this pattern when the user asks for multiple alternatives for an entire existing application rather than one screen.

## Evidence intake

1. Confirm the exact application and public route.
2. Inspect the route map, global shell/navigation, shared styles, and 2–3 representative high-value workflows (for example dashboard, transactions, receipts, settings).
3. If the deployed app is authentication-gated or rendered browser inspection is unavailable, use source inspection to establish information architecture and behavior. State that limitation; do not invent unseen screens.

## Comparison artifact

A single self-contained switchable HTML review artifact is appropriate when comparing coherent **design systems**. Each direction must alter visual stance, typography, color, density, surface treatment, navigation, data hierarchy, and responsive behavior—not merely accent color.

Use realistic product content, preserve recognizable core actions, and include visible interaction plus keyboard focus states. If route-level UX or workflow architecture differs between alternatives, use separate multi-page variants instead; a theme switcher would hide meaningful structural differences.

## Delivery

- Name directions by stance, not letters alone.
- Give each a concise best-fit audience and trade-off.
- Recommend one direction.
- Keep the work review-only until implementation is explicitly approved.
- Publish through the project’s review-artifact route and preserve a repository source copy.

## Verification floor

Deterministically assert all directions are switchable; viewport, mobile breakpoint, reduced-motion, and focus-visible hooks exist; representative core actions exist; interaction changes visible state; and local/public routes succeed when publication is claimed. Rendered desktop/mobile review remains preferred: HTTP success and source assertions verify delivery and mechanics, not visual quality.
