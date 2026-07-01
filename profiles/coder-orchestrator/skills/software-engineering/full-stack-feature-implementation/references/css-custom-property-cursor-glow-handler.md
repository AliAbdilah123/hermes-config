# CSS custom-property cursor glow requires JS handler

Use when a component uses a CSS class whose `::before`/`::after` pseudo-elements depend on JS-driven CSS custom properties (e.g. `--hero-pointer-x`, `--hero-pointer-y`) for interactive effects like cursor-following mist/glow.

## The bug pattern

A CSS class (e.g. `.hero-search`) defines pseudo-elements with `radial-gradient(circle at var(--hero-pointer-x) var(--hero-pointer-y), ...)`. The custom properties have CSS defaults (e.g. `50% 42%`), so the glow renders at a static position. The effect only follows the cursor when a JS `onPointerMove` handler updates those properties:

```ts
function moveHeroGlow(e: PointerEvent<HTMLElement>) {
  const rect = e.currentTarget.getBoundingClientRect()
  e.currentTarget.style.setProperty('--hero-pointer-x', `${e.clientX - rect.left}px`)
  e.currentTarget.style.setProperty('--hero-pointer-y', `${e.clientY - rect.top}px`)
}
```

When a page or component uses the CSS class but omits the handler, the glow silently stays at the default position — no error, no warning, just a static glow that doesn't follow the cursor. This commonly happens after a page split: the original component (e.g. `HeroSearch.tsx`) has the handler, but the page that receives `className="hero-search"` (e.g. `DiscoveryPage.tsx`) does not.

## Fix checklist

1. Check the CSS class definition for `var(--*-pointer-*)` custom properties.
2. Find the component that originally defined the `onPointerMove` handler.
3. Add the same handler to the new/affected component.
4. Import the `PointerEvent` type from React (`type PointerEvent` inline or separate import).

## Full-screen hero with sticky nav

When making a hero section fill the viewport, account for the sticky TopNav height. Komuna's TopNav is `position: sticky; top: 0; height: 68px`. Use:

```tsx
style={{ minHeight: 'calc(100vh - 68px)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
```

The `calc(100vh - 68px)` ensures hero + nav = exactly one viewport. Flex centering vertically centers content within the full-height section.

## Komuna-specific details

- `.hero-search` class in `globals.css` (~line 169) defines `--hero-pointer-x/y` defaults and `::before`/`::after` pseudo-elements.
- `::before` is a static batik pattern (no JS needed).
- `::after` is the cursor-following glow — needs the `onPointerMove` handler.
- `HeroSearch.tsx` (used on SearchProgramsPage) has the handler; `DiscoveryPage.tsx` has inline hero markup with the same class but needed the handler added.
- Responsive CSS overrides `.hero-search` padding with `!important` at mobile breakpoints; inline `minHeight` is not overridden.
