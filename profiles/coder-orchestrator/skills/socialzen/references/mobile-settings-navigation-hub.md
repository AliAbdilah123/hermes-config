# Mobile Settings navigation hub

When the mobile Settings page still shows tab content below the settings list, the root cause is usually that `SettingsPage.tsx` is treating the mobile list as tabs instead of routes.

## Correct SocialZen pattern

- Keep desktop/tablet settings unchanged: `/app/settings?tab=<section>` can continue to drive the existing left-nav/tabbed layout.
- Add dedicated section routes in `apps/frontend/src/App.tsx`:
  - `/app/settings`
  - `/app/settings/:section`
- Keep those routes explicit. Avoid replacing them with only `settings/*` or leaving duplicate wildcard + param routes; explicit root/detail routes make it obvious that the hub and detail pages are separate screens.
- In `apps/frontend/src/pages/settings/SettingsPage.tsx`:
  - Use `useParams()` for `section` and validate it against the shared `SETTINGS_SECTIONS` list.
  - Mobile `/app/settings` renders **only** the list/hub. Do not render `renderContent()` on this route.
  - Mobile `/app/settings/:section` renders **only** the selected existing settings component plus a back header/button to `/app/settings`.
  - Desktop still renders the existing sidebar and `renderContent()` so tablet/desktop behavior remains unchanged.
  - Redirect legacy deep links like `/app/settings?tab=accounts` to `/app/settings/accounts` with `navigate(..., { replace: true })`.
- Update internal links such as reconnect banners from `/app/settings?tab=accounts` to `/app/settings/accounts`.
- AppLayout already hides bottom navigation for `pathname.startsWith("/app/settings")`; preserve that for all settings pages.

## Verification

- Run the targeted settings test, typecheck, and production build:
  - `pnpm exec vitest run src/pages/settings/SettingsPage.test.tsx`
  - `pnpm typecheck`
  - `pnpm build`
- Deploy frontend to `/var/www/html/projects/socialzen/`.
- Verify the deployed SettingsPage bundle is served as `application/javascript` and contains route/list markers such as `Settings sections` and `/app/settings/`.

## Pitfall

Do not leave a mobile `<div className="md:hidden">` list beside an always-rendered content container. Even if the list looks correct, the selected tab's content will still appear underneath on phones.