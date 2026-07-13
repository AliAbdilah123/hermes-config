# SocialZen mobile navigation shell

Use when changing SocialZen's global app navigation or mobile responsive shell.

## Current structure (as of the mobile-bottom-nav planning session)

- `apps/frontend/src/components/AppLayout.tsx`
  - Renders global banners, the desktop/sidebar grid, and the route `<Outlet />`.
  - Desktop sidebar is wrapped in `hidden md:block` inside `md:grid-cols-[240px_1fr]`.
  - The old mobile primary navigation path was an overlay drawer controlled by `sidebarOpen` and `SidebarContext.openSidebar()`.
  - The app content scrolls inside the AppLayout route-content container, so global bottom spacing belongs there rather than inside every page.
- `apps/frontend/src/components/Sidebar.tsx`
  - Owns the main app nav item list: Dashboard `/app/dashboard`, Calendar `/app/calendar`, Posts `/app/posts`, Analytics `/app/analytics`, Settings `/app/settings`.
  - Also includes desktop/sidebar-only UI: logo, `+ New Post`, user chip, logout, and mobile drawer close button.
- `apps/frontend/src/components/Topbar.tsx`
  - Mobile hamburger uses `SidebarContext.openSidebar()`.
  - If replacing the mobile drawer with another nav, remove/gate this hamburger so it does not become a dead duplicate control.
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
- Keep nav z-index high enough over page content but lower than modals/drawers; around `z-40` is usually sufficient.
- Validate with `pnpm typecheck`, `pnpm build`, and viewport checks below/above `md`.

## Plan/review artifact expectation

For plan-only requests, inspect these files read-only, save the markdown plan under `/home/ubuntu/socialzen/.hermes/plans/`, publish a styled review HTML under `/usr/share/nginx/html/prds/socialzen/`, verify HTTP 200, and explicitly state that no code was implemented or deployed.