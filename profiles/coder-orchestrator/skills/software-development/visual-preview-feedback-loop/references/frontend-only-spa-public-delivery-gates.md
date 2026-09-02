# Frontend-only SPA public delivery gates

Use this for standalone React/Vite-style prototypes published under an isolated subpath.

## Subpath routing is a source concern

A successful `vite build --base=/projects/example/` fixes emitted asset URLs but does **not** fix client-side navigation. Configure the router from the same base:

```tsx
const basename = import.meta.env.BASE_URL.replace(/\/$/, '');
<BrowserRouter basename={basename}>…</BrowserRouter>
```

Include Vite ambient types if TypeScript does not know `ImportMeta.env`:

```ts
/// <reference types="vite/client" />
```

Verify a deep link and in-app navigation remain under the public prefix. Root HTTP 200 and valid assets are insufficient.

## Never let deployment mask verification failure

A compound shell can return success when a failed verifier is followed by a successful copy. Put `set -euo pipefail` in the outer shell as well as the verifier, and deploy only after verification returns zero:

```bash
set -euo pipefail
verify_script=$(mktemp /tmp/hermes-verify-spa-XXXXXX.sh)
trap 'rm -f "$verify_script"' EXIT
"$verify_script"
rsync -a --delete dist/ "$publish_root/"
```

## Functional E2E and pixel review are separate hard gates

Run public browser behavior with console/page/request failure capture and overflow checks. Then inspect fresh screenshots from the exact public URL. Treat visual findings as failures even when E2E is green.

Check tablet-first operational apps for category reachability, complete unavailable labels, >=48px touch targets, accessible mobile cart/payment actions, cohesive formula units, content-sized badges, aligned repeated cards, and readable secondary copy.

After a visual fix: rebuild, republish, rerun the complete public matrix, and capture fresh screenshots. Local or coding-agent screenshots are not final evidence.

## Full-viewport modals need the correct DOM boundary

`position: fixed; inset: 0` can still compete with app-shell chrome when rendered inside an ancestor stacking context. Render app modals through a body-level portal:

```tsx
return createPortal(<div className="modal-backdrop">…</div>, document.body);
```

Verify the backdrop dims the entire viewport, including sticky headers and focused skip links.

## Public-cache classification

If the public root initially returns a stale 404 while new assets are reachable, retry the root with a cache-busting query and verify semantic markers plus namespaced asset URLs. Keep root, asset, and browser behavior as separate evidence boundaries.
