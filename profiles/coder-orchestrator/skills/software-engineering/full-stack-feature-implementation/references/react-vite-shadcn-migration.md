# React/Vite shadcn Migration Notes

Use when a user asks to move an existing React/Vite frontend from custom CSS/widgets to a real shadcn-style setup.

## Practical sequence

1. Install the shadcn/Tailwind/Radix dependencies in the frontend package:
   ```bash
   npm install class-variance-authority clsx tailwind-merge lucide-react \
     @radix-ui/react-slot @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
     @radix-ui/react-select tailwindcss @tailwindcss/vite tw-animate-css
   ```
2. Add `components.json` with aliases for `components`, `ui`, `lib`, and `utils`.
3. Add `src/lib/utils.ts` with the canonical `cn(...inputs)` helper using `clsx` + `tailwind-merge`.
4. Add real shadcn-compatible primitives under `src/components/ui/` instead of only styling old components to look similar. Common minimum set:
   - `button.tsx` with `cva` variants and Radix `Slot`
   - `card.tsx`
   - `input.tsx`
   - `label.tsx`
   - `dialog.tsx` using `@radix-ui/react-dialog`
   - `dropdown-menu.tsx` using `@radix-ui/react-dropdown-menu`
   - `select.tsx` using `@radix-ui/react-select`
5. Wire Tailwind v4 into Vite:
   ```ts
   import tailwindcss from '@tailwindcss/vite'
   // plugins: [react(), tailwindcss()]
   ```
6. Put Tailwind v4 + shadcn CSS variables at the top of the app stylesheet:
   ```css
   @import "tailwindcss";
   @import "tw-animate-css";
   @custom-variant dark (&:is(.dark *));
   @theme inline { /* map --color-* tokens to CSS variables */ }
   :root { --radius: .625rem; --background: ...; --primary: ...; }
   @layer base { * { border-color: var(--border); } body { background: var(--background); color: var(--foreground); } }
   ```
7. Migrate interactive primitives, not just visuals:
   - Custom modal/backdrop → shadcn/Radix `Dialog`
   - Custom avatar/menu state → shadcn/Radix `DropdownMenu`
   - Native selects can remain temporarily, but prefer shadcn `Select` when time allows.
8. Keep compatibility wrappers if the app has many existing `Button`, `Card`, or `TextInput` call sites. Wrap shadcn primitives in the existing component API, mapping legacy class names to shadcn variants, then migrate call sites incrementally.
9. Verify with tests and production build, then deploy and confirm public asset hashes are served from nginx/CDN.

## Pitfalls

- Do not call a UI “fully migrated to shadcn” if it only copies shadcn-like CSS. Add `components.json`, `cn`, Tailwind plugin/theme variables, and actual Radix-backed primitives.
- Radix dropdowns are modal by default in some interaction contexts and can hide the rest of the page from Testing Library queries while open. For a header avatar menu that should not lock the page, use `<DropdownMenu modal={false}>`.
- Existing tests that query a custom menu/backdrop may need to be updated for Radix roles/portals and new user flow.
- Tailwind v4 uses `@tailwindcss/vite` and CSS `@theme`; do not assume a Tailwind v3 `tailwind.config.js` is required.
