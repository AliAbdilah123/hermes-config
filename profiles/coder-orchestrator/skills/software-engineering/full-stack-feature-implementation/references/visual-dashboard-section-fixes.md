# Visual dashboard section fixes from screenshot feedback

Use when a user provides ordered screenshots with UI defects in a React/Vite dashboard and asks to fix them directly.

## Pattern

1. Map each screenshot in order to the exact component and CSS selector before editing. Keep the fix scoped to those sections unless the defect is from a shared primitive.
2. For bulky connection/status panels (for example WhatsApp QR/status), prefer moving the operational detail into a modal and exposing a compact status pill beside the page/section title. The pill should open the modal and reflect current status (`Connected`, `Belum terhubung`, etc.).
3. Sidebar collapse affordances often read better when the button straddles the sidebar edge: position it absolute from the sidebar header, use a circular/pill shape, white/bright border, and hide it on mobile drawer widths.
4. Header action buttons in legacy panels need explicit height, padding, inline-flex alignment, gap, and responsive wrapping. Do not rely on generic table/button styles.
5. When a converted shadcn/legacy card looks visually inconsistent, normalize surface colors back to the app tokens (`#fff`/`#f8fbff`, `--line`, blue primary) instead of introducing a new dark/gray section palette.
6. Table action columns can show broken row separators if action cells use flex and the table is fixed-width. Keep the `td` border, align buttons with `height:100%`, and remove only the final row's final border.
7. Opportunity/list rows with chips commonly overlap because grid columns are too rigid. Use `minmax(0,…)`, `min-width:0`, wrapping chip containers, ellipsis only on the primary name, and collapse secondary fields/actions under the name at narrower breakpoints.

## Verification

- Run the project build (`npm run build` for Vite projects).
- Deploy the built assets to the actual nginx-served directory, then curl public/local index and asset URLs to verify new hashes.
- Grep deployed JS/CSS for durable markers from the fix (new class names or modal/pill labels) when the SPA index does not contain rendered text.
- Commit only the touched source files if the working tree already has unrelated changes; report any push blocker such as a missing remote without treating it as a durable project fact.
