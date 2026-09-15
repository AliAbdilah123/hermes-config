# Dual-target Vite SPA deployment

Use when one Vite/React repository serves both a root-domain deployment (for example Vercel at `/`) and a server-mounted subpath (for example nginx at `/projects/app/`). A single hardcoded base can make one target blank while the other works.

## Three independent routing boundaries

Keep these aligned per target:

1. **Generated asset base** — Vite's `base` controls emitted JS/CSS URLs.
2. **Client router basename** — React Router must consume the same effective base, preferably `import.meta.env.BASE_URL`, rather than repeating a literal.
3. **Host SPA fallback** — direct navigation to `/posts` or another client route must rewrite to `/index.html` on the root-domain host (for Vercel, a `vercel.json` rewrite).

Minimal pattern:

```ts
// vite.config.ts
export default defineConfig({
  base: process.env.VERCEL ? "/" : "/projects/app/",
})
```

```tsx
<BrowserRouter basename={import.meta.env.BASE_URL}>
```

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

Use an explicit build variable instead of `VERCEL` when there are more than two deployment targets or local builds need root-base output.

## Verification matrix

Build both modes independently and inspect generated `dist/index.html`:

- Root-domain build emits `/assets/...`.
- Subpath build emits `/projects/app/assets/...`.
- Both referenced JS/CSS URLs return 200 with correct MIME types on their respective hosts.

Then test with a real browser:

- Root `/` renders actual page content, not merely toast/notification containers.
- Direct client routes such as `/posts`, `/about`, and `/leaderboard` render after a fresh navigation.
- Subpath root and direct subpath routes still render.
- No uncaught runtime or failed-resource errors.

A loaded entry bundle is not sufficient: a wrong `basename` can initialize React while rendering no route. A working homepage is not sufficient: missing host rewrites can still make direct routes return a platform 404.

## Deployment-status discovery

Do not assume GitHub Actions owns deployment. If `gh workflow list` and `gh run list` are empty, inspect commit statuses and deployments:

```bash
gh api repos/OWNER/REPO/commits/SHA/status
gh api repos/OWNER/REPO/deployments --jq '.[] | [.sha,.environment,.created_at]'
```

A provider such as Vercel may report deployment through a commit status while no Actions workflow exists. Wait for that exact commit's provider status, then verify the public artifact and browser behavior.

## Hashed-asset retention

For self-managed static deployments, avoid deleting the immediately previous content-hashed JS/CSS generation while cached HTML can still reference it. Deploy additively or retain at least one prior generation, and make HTML non-cacheable/revalidating. Otherwise old HTML may request deleted assets and receive a SPA fallback document as JavaScript, producing a blank page.
