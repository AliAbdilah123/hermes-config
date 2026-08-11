# Meta OAuth callback routing and low-friction disconnect UX

Use this when Facebook/Instagram OAuth succeeds but the browser lands on a bare project prefix, retains Meta's `#_=_` fragment, or enters an nginx redirect loop; also when disconnect UI unnecessarily requires a typed phrase.

## OAuth callback diagnosis

1. Inspect the **effective runtime** `FrontendBaseURL`, including fallback precedence. A host-only value sourced from `ALLOWED_ORIGIN` can be mistaken for a root-mounted frontend even though SocialZen is mounted at `/projects/socialzen`.
2. Compare the callback's exact `Location` header with the actual SPA mount and route. The connected-account destination is `/projects/socialzen/app/settings/accounts`, not a root `/app/settings...` path or the bare project prefix.
3. Probe both `/projects/socialzen` and `/projects/socialzen/` publicly with redirects disabled. Canonicalize the no-slash path once to the slash path; ensure the catch-all does not redirect the slash form back to the no-slash form.
4. Clear Meta's inherited fragment explicitly in the callback redirect (for example, a terminal empty `#`). URL fragments are browser-side and never reach Go/nginx, so server logs cannot prove they disappeared.
5. Add focused tests for: host-only frontend base, already-prefixed base (no duplicate prefix), exact connected-accounts route, and a callback `Location` that clears the fragment.
6. After deploy, verify the public callback's `Location`, the service health endpoint, and the live lazy route/bundle. An HTTP 200 on the app root is insufficient.

## Disconnect UX

A destructive confirmation dialog is already an explicit confirmation step. Do not require typing `DISCONNECT` unless the operation is unusually broad or irreversible and the user explicitly wants that friction.

For SocialZen account disconnection:
- Keep the impact preflight and consequences summary.
- Enable the destructive button once impact data loads.
- Remove the confirmation input and request-body phrase.
- Remove backend phrase validation too; frontend-only removal leaves the action broken.
- Preserve ownership checks, idempotency, history retention, provider revocation, notification delivery, and detailed response behavior.
- Regression-test both UI button behavior and a bodyless authenticated DELETE lifecycle.

## Deployment boundary

SocialZen production requires both artifacts: rebuild/restart the Go binary used by systemd and copy the clean frontend `dist/` to `/var/www/html/projects/socialzen/`. Pushing Git alone changes neither runtime artifact.
