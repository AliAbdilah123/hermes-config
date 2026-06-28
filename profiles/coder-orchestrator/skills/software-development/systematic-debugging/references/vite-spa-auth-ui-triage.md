# Vite SPA Auth UI Triage

Use this when a deployed Vite/React SPA auth route renders the wrong auth experience (fallback form instead of provider UI) or a partial/skeleton UI such as a single horizontal line.

## Durable lessons

1. **Check build-time env at the app build root.** Vite only exposes `VITE_*` variables at build time and auto-loads env files relative to the directory running `vite build` (commonly `apps/web`). A root project `.env` is not automatically available if the build runs in `apps/web`.
2. **Verify the deployed bundle, not just source/env files.** Inspect the served HTML asset name and the served JS for proof that provider URLs were compiled in and are not `undefined`/fallback expressions.
3. **Provider UI needs provider context and CSS.** For Neon Auth UI, rendering `<AuthView />` alone can produce an incomplete card/separator. The app must import `@neondatabase/auth-ui/css` (or the Tailwind variant) and wrap the tree with `NeonAuthUIProvider` using the Neon auth client.
4. **Preserve local fallback intentionally.** If the app supports a local first-party login fallback, keep it behind an explicit provider-config check so missing provider env still gives a deterministic fallback rather than a broken provider UI.

## Quick verification recipe

- Confirm env is present where Vite builds:
  - `apps/web/.env.local` or exported env must include `VITE_NEON_AUTH_URL`.
- Build from the web app directory.
- Publish `dist/` to the static web root.
- Fetch the public auth page HTML and identify the current JS/CSS assets.
- Probe the public JS bundle for:
  - provider URL/domain present
  - no compiled `undefined` auth URL expression
  - provider/context markers present when expected
- Probe the rendered DOM (browser/headless) for actual form markers such as `Sign In`, `Email`, and `Password`, not just that the route returns 200.
