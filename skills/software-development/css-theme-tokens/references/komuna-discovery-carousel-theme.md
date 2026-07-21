# Discovery hero theme verification

Reproduced issue: discovery carousel caption stayed visually dark in light mode
because the gradient was `rgba(0,0,0,.88)`.

Fix location: `apps/web/src/globals.css`

Quick grep checks after changing discovery carousel theming:
- caption gradient uses `color-mix(in oklch, var(--ink-1) 88%, transparent)`
- carousel border uses `var(--rule)` instead of `oklch(1 0 0 / .24)`
- dot outline/fill uses `var(--ink-1)` instead of `white`

Tests that guard this behavior:
- `__tests__/DiscoveryMobileParity.test.ts`
- `components/discovery/__tests__/DiscoveryHeroCarousel.test.tsx`