# Settings navigation + theme toggle behavior

When updating SocialZen Settings navigation or theme controls:

- Keep visitor-facing theme toggle on Landing only (`pages/landing/LandingNav.tsx`).
- Do not put `ThemeToggle` in authenticated global chrome (`components/Topbar.tsx`), because that makes it appear on Dashboard, Analytics, Profile, Connected Accounts, and other authenticated pages.
- Place the authenticated Light/Dark control inside `Settings → Accessibility` (`pages/settings/SettingsPage.tsx`). The existing `ThemeProvider` already persists `localStorage.theme` and applies `.dark` across sessions; do not add backend persistence unless cross-device sync is explicitly requested.
- Main Settings back button should preserve entry context with browser/app history (`navigate(-1)`) and only fall back to Dashboard if no prior route exists.
- Settings subpage back buttons should always return to `/app/settings` and use `{ replace: true }` so the subpage does not remain immediately behind the main Settings page in history. This prevents Settings hub → Back from bouncing back into the subpage.
- Every routed Settings subpage should expose a simple header with Back + page title. Mobile has the sticky header; desktop should have an in-card header when `pathSection` is present.

Verification checklist:

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck && pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
js=$(basename $(ls /var/www/html/projects/socialzen/assets/SettingsPage-*.js | head -1))
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$js" | grep -iE 'HTTP/|content-type|cf-cache-status'
grep -q "Light/Dark Mode" "/var/www/html/projects/socialzen/assets/$js"
```

Expected: Settings bundle is `application/javascript` and contains the Settings-only theme marker.
