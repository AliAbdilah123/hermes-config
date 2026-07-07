# Komuna program hero/session card visual tweaks

Use when adjusting Komuna public program detail hero content density or the session cards shown in the hero/upcoming sessions areas.

## Files to inspect

- `apps/web/src/pages/program-detail/HeroSection.tsx` — immersive public program hero typography, spacing, stats, CTA spacing.
- `apps/web/src/pages/program-detail/mobile.css` — mobile overrides for hero height, hero text, stats, and hero session cards.
- `apps/web/src/pages/program-detail/HeroRightSessions.tsx` — stacks compact cards in the hero sessions column.
- `apps/web/src/pages/all-sessions/SessionCardCompact.tsx` — compact horizontal hero/upcoming session card.
- `apps/web/src/pages/all-sessions/SessionCard.tsx` — larger all-sessions card; keep manager fallback safe here too.
- `apps/web/src/__tests__/all-sessions/SessionCardCompact.test.tsx` — cheap regression for card image sizing and manager fallback.

## Patch pattern

1. For “image card wider / rectangle” requests, confirm orientation. If the user says “3:4” but also says wider horizontally, implement it as a wide rectangle where height is 3/4 of width: CSS `aspectRatio: '4 / 3'` (not portrait `3 / 4`). Update both desktop inline sizing in `SessionCardCompact.tsx` and mobile overrides in `program-detail/mobile.css`.
   - Example desktop: grid column/image width `176px`, `aspectRatio: '4 / 3'` (176×132 rendered box).
   - Example mobile: grid column/image width `132px`, `aspect-ratio: 4 / 3`.
   - Keep the rail card wider too (e.g. flex basis around `min(580px, 90vw)`) so the horizontal image and single-line datetime have room.
2. If manager may be missing, compute a local display name before rendering:
   - `const managerName = session.managerName || 'null manager'`
   - Use it for avatar alt text, initial fallback, and visible label.
   - Do not call `session.managerName.charAt(0)` directly; empty strings produce bad fallback UI.
3. For hero content that covers too much background, reduce the inline hero values in `HeroSection.tsx` and the mobile overrides together:
   - Lower hero `minHeight`/padding.
   - Lower title clamp max and viewport factor.
   - Lower description font size/line-height/max width and tighten action/stats margins.
4. Keep the change CSS/inline-only unless data shape is missing; do not refactor the hero composition for a visual density tweak.

## Verification

Run from `apps/web`:

```bash
npm run test -- SessionCardCompact
unset VITE_NEON_AUTH_URL
npm run build
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/
sudo chown -R www-data:www-data /var/www/html/projects/komuna/
```

Then verify deployed asset markers rather than expecting SPA text in `index.html`:

```bash
JS=$(curl -sS https://komuna.ahsanworks.com/ | grep -o 'assets/index-[^"[:space:]]*\.js' | head -1)
CSS=$(curl -sS https://komuna.ahsanworks.com/ | grep -o 'assets/index-[^"[:space:]]*\.css' | head -1)
curl -sS "https://komuna.ahsanworks.com/$JS" | grep -o 'null manager\|176px minmax' | sort -u
curl -sS "https://komuna.ahsanworks.com/$CSS" | grep -o '96px minmax\|min-height:540px' | sort -u
```

Commit/push only the touched frontend files; leave unrelated in-flight backend/doc changes alone.