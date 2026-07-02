# SPA Subpath Asset Base / Domain Routing Blank Page

Use when a deployed Vite/React SPA is served under a subpath (for example `/projects/<app>/`) and the browser shows a blank page with no visible app UI.

## Durable symptom

- Public route HTML returns `200`, but app stays blank.
- HTML references root assets like `/assets/index-*.js` while the app is mounted at `/projects/<app>/`.
- Domain-specific nginx config may differ from the IP/default config: one server block may rewrite or sub_filter asset paths while the domain block does not.
- Cloudflare/mobile browsers can cache the old HTML, so verification should use a cache-busted URL.

## Triage recipe

```bash
curl -k -sS -L -D /tmp/app.headers 'https://domain/projects/app/?v=probe' -o /tmp/app.html
python3 - <<'PY'
from pathlib import Path
s = Path('/tmp/app.html').read_text(errors='ignore')
print(s[:1200])
PY
grep -oE 'src="[^"]+|href="[^"]+' /tmp/app.html | head -20

# Probe both possible asset locations
curl -k -sS -I 'https://domain/assets/index-HASH.js' | sed -n '1,8p'
curl -k -sS -I 'https://domain/projects/app/assets/index-HASH.js' | sed -n '1,8p'
```

Also inspect all relevant nginx server blocks, not just the IP/default block:

```bash
grep -R "server_name .*domain\|projects/app\|sub_filter" -n /etc/nginx/sites-enabled /etc/nginx/conf.d /etc/nginx/projects 2>/dev/null
```

## Fix pattern

Prefer building the SPA with the correct Vite base over relying on nginx HTML rewriting:

```ts
// vite.config.ts
export default defineConfig({
  base: process.env.VITE_BASE || "/projects/app/",
})
```

Then rebuild and publish the built `dist/` directory to the subpath document root.

## Verification

- Fetch cache-busted public HTML and confirm asset URLs begin with `/projects/app/assets/`.
- Fetch main JS/CSS asset URLs and confirm `200` plus correct content types (`application/javascript`, `text/css`).
- If a browser automation tool times out, verify with HTTP asset probes rather than concluding the app is still broken.
- Tell the user to force-refresh/clear site cache if mobile Brave/Cloudflare may have cached old HTML.
