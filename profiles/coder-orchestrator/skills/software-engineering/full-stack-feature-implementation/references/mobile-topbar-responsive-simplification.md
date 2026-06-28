# Mobile topbar responsive simplification

Use this reference when a user asks to reduce unnecessary navigation in a mobile topbar/header for a deployed React/Vite SPA.

## Pattern

1. Identify whether there are multiple topbars:
   - Public/site topbar (for discovery/marketing/auth pages).
   - Dashboard/app-shell topbar (for logged-in workspace pages).
2. Preserve only mobile-essential controls in the visible topbar:
   - Brand/home context.
   - Auth actions for guests, compressed into one row.
   - Notification/profile/account access for authenticated users.
   - Required context switchers only when they are needed to use the current screen (for example manager product selector).
3. Move or hide secondary controls at narrow breakpoints:
   - Dashboard shortcut if it is already available in the profile menu or drawer.
   - Theme toggle.
   - Language switcher.
   - Long profile display name.
4. Prefer CSS breakpoint changes over duplicating component trees:
   - Convert wrapped mobile topbars to a single-row layout (`flex-wrap: nowrap` or a compact grid).
   - Hide secondary controls with explicit classes so desktop behavior remains unchanged.
   - Remove horizontal-scroll control strips unless the user explicitly wants swipeable nav.
5. Verify after deployment:
   - Production build succeeds.
   - Public index references the new asset hashes and JS/CSS assets return 2xx.
   - Use a 390px-ish headless screenshot to confirm no extra nav row/horizontal overflow and that only necessary topbar controls remain.

## Reporting

If full lint fails because of unrelated repo-wide debt, still run and report the production build plus the scoped public/mobile screenshot verification. Do not fix broad lint debt during a narrow visual/mobile topbar task unless asked.
