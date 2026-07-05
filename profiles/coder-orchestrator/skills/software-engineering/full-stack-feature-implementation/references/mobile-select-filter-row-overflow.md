# Mobile select/filter row overflow in React/Vite dashboards

Use when a newly-added native `<select>` or filter control is too wide on mobile and pushes a dashboard/header row outside the viewport.

## Pattern

1. Fix the shared row sizing first, not individual screenshots only:
   - Parent row: `display:flex`, small mobile `gap`, `min-width:0`.
   - Left/control group that should shrink: `flex:1`, `min-width:0`.
   - Fixed right-side select/action: set explicit mobile `width` + `flex:0 0 <width>` instead of large `min-width`.
2. If a child component has Tailwind `min-w-*` classes, pass a scoped class and override narrowly:
   - `.wallet-filter { min-width:0 !important; max-width:<mobile cap>; }`
   - Restore larger caps at `min-width:640px`.
3. Keep the native select; do not replace it with a custom dropdown just for width control.
4. Verify with:
   - project build
   - deployed bundle marker for the scoped class
   - mobile screenshot/headless visual check for no horizontal overflow.

## Example

```css
.top-controls { display:flex; gap:8px; min-width:0; }
.period-and-wallet { display:flex; gap:8px; flex:1; min-width:0; }
.view-select { width:92px; flex:0 0 92px; }
.wallet-filter { min-width:0 !important; max-width:112px; }

@media (min-width:640px) {
  .view-select { width:148px; flex-basis:148px; }
  .wallet-filter { max-width:180px; }
}
```
