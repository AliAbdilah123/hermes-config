# Existing Google Material Symbols icon font in React/Vite apps

Use when a UI already loads Google Fonts Material Symbols and a small visual fix needs icons made consistent with the rest of the app.

## Pattern

1. Check `index.html` for the loaded font URL, e.g. `Material+Symbols+Outlined`.
2. Check global CSS for the reusable class, usually:

```css
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```

3. Replace ad-hoc Unicode glyphs or emoji-like text icons with Material Symbols ligature names:

```tsx
function MenuIcon({ children }: { children: string }) {
  return (
    <span className="material-symbols-outlined" aria-hidden="true">
      {children}
    </span>
  )
}
```

Example mappings:

- profile/user: `person`
- wallet: `account_balance_wallet`
- booking/session list: `event_note`
- dashboard: `dashboard`
- logout: `logout`
- dropdown chevron: `expand_more`

## Verification

- Run the app's normal frontend build.
- Deploy the Vite `dist/` to the currently served web root.
- Verify the deployed JS bundle contains the icon ligature names and `material-symbols-outlined`.

## Pitfall

Do not add a new icon package for this. If the font is already loaded, the lazy fix is to use the existing ligature class and keep the diff local to the component.
