# Komuna approved public program-detail redesign workflow

Use when the user approves a visual redesign for Komuna's public `/programs/:id` detail page from a static/proposal artifact.

## Durable lessons

- Preserve Komuna's existing theme variables; do not paste external Tailwind CDN theme tokens or hardcode a new palette. Use `var(--paper-*)`, `var(--ink-*)`, `var(--accent)`, and `var(--rule)` so dark/earth theme stays intact.
- Treat the supplied HTML/design as composition guidance only: hero layout, title treatment, chips, stat strip, session rail, package section. Keep existing data fetches and membership/booking/package behaviors untouched.
- For public program detail, prefer moving dense upcoming sessions out of the hero right column into a below-hero horizontal rail when the approved design calls for an immersive hero.
- Keep API fetch safety explicit: verify the exact public program ID/slug exists before checking the page. For Komuna seed data, `prog-yoga` is a stable public program id; old test ids like `p1` may return `{"error":"not_found"}` publicly.
- Komuna's primary public domain is root-based (`https://komuna.ahsanworks.com/...`). The `/projects/komuna/...` subpath is also routed in nginx but can inject a subpath basename and produce misleading page-not-found behavior in headless checks. Verify the user-facing domain route first.

## Verification pattern

After implementation:

```bash
cd /home/ubuntu/projects/komuna/apps/web
npm run test -- ProgramDetailPage
env -u VITE_NEON_AUTH_URL npm run build
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/
sudo chmod -R a+rX /var/www/html/projects/komuna
curl -sI https://komuna.ahsanworks.com/programs/prog-yoga | head -1
curl -s https://komuna.ahsanworks.com/api/v1/programs/prog-yoga | grep 'Balikpapan Coastal Yoga Studio'
curl -s 'https://komuna.ahsanworks.com/api/v1/programs/prog-yoga/sessions?status=upcoming&page=1&limit=3' | grep 'items'
curl -s https://komuna.ahsanworks.com/api/v1/programs/prog-yoga/packages | grep 'pkg-yoga'
timeout 60 chromium-browser --headless --no-sandbox --disable-gpu --virtual-time-budget=8000 --dump-dom https://komuna.ahsanworks.com/programs/prog-yoga > /tmp/komuna_prog_dom.html 2>/tmp/komuna_chrome.log
grep -o 'Balikpapan Coastal Yoga Studio' /tmp/komuna_prog_dom.html | head -1
grep -Ei 'failed to fetch|api error|error loading|program not found' /tmp/komuna_prog_dom.html /tmp/komuna_chrome.log | head -20 || true
```

Ignore Chromium DBus/AppArmor/GPU noise in stderr when the DOM loads correctly; it is not an app fetch/API error.

## Commit/push pitfall

The repo remote may be SSH while GitHub SSH egress is blocked. If `git push` times out on port 22 and `gh auth status` shows HTTPS token auth is available, push via HTTPS rewrite without changing the repo remote:

```bash
git -c url.https://github.com/.insteadOf=git@github.com: push origin <branch>
```
