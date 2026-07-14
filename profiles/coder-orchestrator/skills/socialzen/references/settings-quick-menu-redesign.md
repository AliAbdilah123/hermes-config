# Settings quick menu redesign

Use this when redesigning SocialZen Settings navigation into a compact horizontal quick menu.

## Pattern

- Keep existing Settings section components and API helpers unchanged; only replace the navigation shell.
- Use a reusable `SettingsQuickMenu` component near `SettingsPage.tsx` unless it is needed elsewhere.
- Section config should carry `value`, translated `labelKey`, and a Lucide `icon` so nav rendering stays data-driven.
- Desktop: one horizontal row with equal/flexible items.
- Mobile: horizontal `overflow-x-auto` rail with hidden scrollbars:
  - `[-ms-overflow-style:none]`
  - `[scrollbar-width:none]`
  - `[&::-webkit-scrollbar]:hidden`
- Use `aria-label` on the nav, `aria-current="page"` on the active button, visible focus rings, and icons marked `aria-hidden`.
- For smooth click behavior: set active state optimistically, navigate to `/app/settings/:section`, then `requestAnimationFrame(() => element.scrollIntoView({ behavior: "smooth", block: "start" }))`.
- For active highlight while scrolling: observe the rendered section with `IntersectionObserver`; fall back to route-derived active section if the observer is unavailable.
- Framer Motion is acceptable here because the UX explicitly requires hover/tap motion; add it to `apps/frontend/package.json` with pnpm and commit the lockfile.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck
pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
curl -sI http://localhost/projects/socialzen/ | head -1
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<SettingsPage chunk>.js" | grep -i content-type
```

Expected JS content-type is `application/javascript`.

## Pitfalls

- Do not preserve the previous desktop left sidebar if the request says to replace the large vertical Settings navigation/cards with a horizontal quick menu.
- Do not remove or rewrite Settings section internals (Profile, Connected Accounts, Billing, Notifications, Accessibility, Danger) unless explicitly requested.
- Mobile Settings previously used a route-hub-only shape. For a quick-menu redesign request, it is acceptable to show the quick menu plus active section content on mobile, because the requested UX is section quick navigation, not a hub list.