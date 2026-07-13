# SocialZen mobile navigation shell

Use when changing SocialZen's global app navigation, mobile responsive shell, or primary app navigation pattern.

## Current structure

- `apps/frontend/src/components/AppLayout.tsx`
  - Renders global banners, the desktop/sidebar grid, and the route `<Outlet />`.
  - Desktop sidebar is wrapped in `hidden md:block` inside `md:grid-cols-[240px_1fr]`.
  - The app content scrolls inside the AppLayout route-content container, so global bottom spacing belongs there rather than inside every page.
- `apps/frontend/src/components/Sidebar.tsx`
  - Owns the desktop sidebar UI: logo, `+ New Post`, main nav, user chip, logout.
  - Do not redesign it for mobile nav changes unless explicitly requested; keep desktop/tablet unchanged.
- `apps/frontend/src/components/Topbar.tsx`
  - Historically had a mobile hamburger that opened `SidebarContext.openSidebar()`.
  - When mobile primary navigation is replaced by bottom nav, remove/gate this hamburger so it is not a dead duplicate control.
  - Desktop right-side actions (theme toggle, Schedule button, avatar) are separate and should remain unchanged unless explicitly requested.
- `apps/frontend/src/pages/settings/SettingsPage.tsx`
  - Settings route is `/app/settings` with internal tabs in query params (`?tab=profile`, `?tab=accounts`, etc.).
  - It has its own desktop and mobile settings navigation. Global mobile bottom nav should not replace that internal settings nav.

## Bottom navigation implementation checklist

- Keep desktop/tablet unchanged by using the existing breakpoint: desktop sidebar stays `hidden md:block`; mobile bottom nav is `md:hidden`.
- Prefer one small `BottomNavigation` component plus small `AppLayout`/`Topbar` edits. Do not rewrite routes or redesign `Sidebar` unless necessary.
- Preserve existing route targets. For active state, handle nested routes by prefix:
  - Dashboard: `/app/dashboard`
  - Calendar: `/app/calendar`
  - Posts: `/app/posts`, including `/app/posts/new` and `/app/posts/:postId/edit`
  - Analytics: `/app/analytics`
  - Settings: `/app/settings`
- If the requirement says Settings should use its own navigation, hide the global bottom nav with `location.pathname.startsWith("/app/settings")`. This must also cover `/app/settings?tab=...`.
- Add safe-area support to the fixed nav with `env(safe-area-inset-bottom)` and add matching mobile-only bottom padding to AppLayout's internal scroll container so content is not covered.
  - Working pattern: bottom nav inline style `paddingBottom: "max(env(safe-area-inset-bottom), 10px)"`.
  - Working content padding: `pb-[calc(84px+env(safe-area-inset-bottom))] md:pb-0` on the internal scroll container, conditional so Settings does not get extra spacing.
- Keep nav z-index high enough over page content but lower than modals/drawers; around `z-40` is usually sufficient.
- Keep the nav accessible: `<nav aria-label="Primary navigation">`, icon labels visible, icon `aria-hidden`, and `aria-current="page"` on the active section.

## Minimal implementation shape that worked

- Create `apps/frontend/src/components/BottomNavigation.tsx`:
  - local nav array with five items is acceptable; do not extract shared nav config unless drift becomes a real issue.
  - use `useLocation()` and `pathname === to || pathname.startsWith(`${to}/`)` for active state.
  - use existing `cn()` helper and existing theme tokens (`bg-primary`, `text-primary-foreground`, `var(--bg)`, `var(--line)`).
- Simplify `AppLayout.tsx`:
  - import `useLocation` and `BottomNavigation`.
  - compute `hideBottomNav = pathname.startsWith("/app/settings")`.
  - render `!hideBottomNav && <BottomNavigation />` after the main grid.
  - remove the old mobile drawer state/context if no caller remains.
- Simplify `Topbar.tsx`:
  - remove the mobile hamburger, `SidebarContext`, and `Menu` import when the drawer is gone.
  - keep desktop actions unchanged.

## Verification and deploy checklist

- Run:
  - `cd /home/ubuntu/socialzen/apps/frontend && pnpm typecheck`
  - `cd /home/ubuntu/socialzen/apps/frontend && pnpm build`
- Deploy frontend only:
  - `sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/`
  - `sudo chown -R www-data:www-data /var/www/html/projects/socialzen`
- Verify:
  - `curl -sI http://localhost/projects/socialzen/ | head -1` returns `HTTP/1.1 200 OK`.
  - The deployed index JS asset returns `content-type: application/javascript`, not `text/html`.
  - Grep the deployed production bundle for stable markers such as `Primary navigation`, `safe-area-inset-bottom`, and `/app/settings` to prove the new shell reached production.
- Commit and push from `/home/ubuntu/socialzen` after deploy.

## Pitfalls

- Do not leave both hamburger drawer and bottom nav on mobile. It creates duplicate navigation, and if the drawer context was removed the hamburger becomes a dead control.
- Do not add bottom padding inside every page. The app scrolls through AppLayout's route-content container, so page-by-page padding will miss pages and create inconsistencies.
- Do not hide Settings by active tab/query param. Pathname prefix is the stable route-level check.
- Do not use exact NavLink matching for Posts; create/edit routes must still highlight Posts.
- Do not touch nginx/backend for frontend-only shell changes; deploy only the built frontend dist.
