# Visual smoke checks for deployed fullstack apps

Use this when a React/Vite app has been built and exposed through nginx under `/projects/<projectName>/`.

## Why

Build/lint/API smoke checks can all pass while the actual page has visible layout problems. In one session, a deployed app passed lint, build, Go tests, nginx config, and API health checks, but a screenshot revealed the header/title area overlapped. The fix required frontend CSS/markup adjustments, then rebuild + redeploy + another screenshot.

## Minimum pattern

1. Run normal checks first:
   - frontend lint/build
   - backend tests/vet
   - `nginx -t`
   - `curl -I http://127.0.0.1/projects/<projectName>/`
   - `curl -s http://127.0.0.1/api/v1/<health-or-real-endpoint>`
2. Capture a headless browser screenshot of the deployed route, not just the dev server.
3. Inspect for obvious user-facing issues:
   - header/hero/title overlap
   - clipped buttons or nav
   - unreadable contrast
   - horizontal overflow
   - broken assets/images/icons
   - empty screens or hydration errors
4. If a visual issue is found, fix frontend source, rebuild, redeploy `dist`, and recapture the screenshot.
5. Only report completion after both HTTP checks and visual smoke pass.

## Good final report shape

Keep it concise:

- list the fixes
- list the real checks that passed
- provide the public URL
- include the commit hash if git was used
