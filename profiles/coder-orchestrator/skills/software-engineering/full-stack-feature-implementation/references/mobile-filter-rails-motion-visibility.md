# Mobile horizontal filter rails and Framer Motion visibility

Use when converting a dense mobile filter sidebar/grid into horizontal swipe rails in a React/Vite app, especially when the filter block is wrapped in `framer-motion` `whileInView`.

## Pattern

- Keep desktop layout unchanged; scope the rail conversion to the mobile media query.
- Use native controls first:
  - category chips should be real `<button type="button">` elements with `aria-pressed`.
  - location choices can keep radio inputs and style the surrounding label as the pill.
- Override both `display` and `flex-direction` in mobile CSS. If the component has inline `flexDirection: 'column'`, `display:flex` alone will still stack vertically.
- Use the existing site tokens rather than introducing a foreign palette: paper/background vars, ink vars, accent/soft-accent vars, rule/border vars.
- Typical rail CSS:
  - `display: flex !important;`
  - `flex-direction: row !important;`
  - `overflow-x: auto; overflow-y: hidden;`
  - `scroll-snap-type: x proximity;`
  - `scrollbar-width: none; -webkit-overflow-scrolling: touch;`
  - children: `flex: 0 0 auto; min-width: max-content; scroll-snap-align: start;`

## Framer Motion pitfall

If the filter block is inside a `motion.aside` with `initial={{ opacity: 0, x: ... }}` and `whileInView`, headless screenshots or mobile viewport verification may capture it before the intersection animation runs, making the filters look missing even though DOM exists.

For critical mobile controls, add a mobile CSS safety override on the motion wrapper:

```css
.discovery-layout > aside {
  opacity: 1 !important;
  transform: none !important;
}
```

This keeps filters visible and avoids verification false-negatives without changing the desktop animation.

## Verification checklist

- Build the Vite bundle; if full `npm run build` is blocked by unrelated TypeScript debt, run the Vite bundler directly and report the full-build blocker separately.
- Deploy fresh static assets and verify public `index.html` references the new CSS/JS hashes.
- Grep public CSS for the rail markers (`scroll-snap-type`, `flex-direction:row`) and public JS for new accessibility markers (`aria-pressed`) when applicable.
- Take a narrow mobile screenshot after deployment; confirm the rails are visible, horizontal, swipe-clipped at the right edge, and theme-consistent.
