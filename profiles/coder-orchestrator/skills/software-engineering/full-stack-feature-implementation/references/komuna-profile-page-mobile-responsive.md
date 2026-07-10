# Komuna Profile Page Mobile Responsiveness

Use when the Komuna `/profile` page looks like a desktop layout on phone: sidebar visible on the left while the identity/details card is clipped to the right.

## Root cause pattern

`ProfilePage.tsx` can use inline styles for its settings layout:

- Desktop grid: `gridTemplateColumns: '180px 1fr'`
- Large desktop gap/padding (`gap: 40`, main padding `48px 56px`)
- Field rows that keep long email/name text unwrapped

On mobile, that fixed sidebar + content grid exceeds the viewport and pushes the main card off-screen.

## Minimal fix shape

Patch `apps/web/src/pages/ProfilePage.tsx` with class hooks around the inline-style elements, then add a small `<style>` block scoped to the page:

- `.profile-settings-layout { grid-template-columns: minmax(0, 1fr) !important; }` under `@media (max-width: 760px)`
- `.profile-settings-sidebar { position: static !important; flex-direction: row !important; overflow-x: auto; }`
- `min-width: 0` on main layout, panel, card shell, and field rows
- `overflow-wrap: anywhere` on displayed email/name values
- reduced mobile main/card padding

Keep desktop behavior unchanged; do not redesign the profile page.

## Regression coverage

Add/keep a small `ProfilePage.test.tsx` assertion that the responsive class hooks render (`profile-settings-main`, `profile-settings-layout`, `profile-settings-sidebar`, `profile-settings-panel`, `profile-field-value`). JSDOM will not prove visual layout, but this prevents losing the hooks that carry the media-query fix.

## Verification/deploy

For Komuna Vite rebuilds, keep Neon Auth disabled:

```bash
cd /home/ubuntu/projects/komuna/apps/web
npm run test -- src/__tests__/ProfilePage.test.tsx
unset VITE_NEON_AUTH_URL && npm run build
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/
```

Then verify the deployed public bundle changed and contains `profile-settings-layout`.
