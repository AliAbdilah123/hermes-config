# Vite Rebuild Env Pollution — Stale VITE_NEON_AUTH_URL

## Problem

When rebuilding a Komuna (or similar Vite SPA) frontend for a small fix (CSS, component tweak), a stale `VITE_NEON_AUTH_URL` value exported in the shell environment leaks into the build. This sets `isNeonAuthConfigured = true` in `lib/auth.ts`, which makes `AuthPage.tsx` render `<AuthView pathname={pathname} />` (the Neon Auth widget) instead of the local email/password form. The Neon widget without its full provider/CSS setup renders as a bare strip — the sign-in page appears broken.

## Root Cause

- `lib/auth.ts` reads `import.meta.env.VITE_NEON_AUTH_URL` at build time.
- Vite inlines all `VITE_*` env vars present in the process environment.
- A previous session may have `export VITE_NEON_AUTH_URL=...` in the shell for a Neon-auth build.
- That export persists across terminal calls in the same session.
- The next rebuild — even for an unrelated CSS change — picks up the stale value.

## Prevention (fragile — see Permanent Fix below)

Before any Komuna frontend rebuild where local basic auth is intended:

```bash
unset VITE_NEON_AUTH_URL
cd apps/web && npm run build
```

Or run the build in a fresh shell / `env -u VITE_NEON_AUTH_URL npm run build`.

> ⚠️ This approach is fragile — the env var leaked twice across sessions despite
> this guidance. If the project has permanently switched to local auth, apply
> the Permanent Fix below instead.

## Permanent Fix — Remove the Deprecated Auth Code Path

When a deprecated auth provider's env var (`VITE_NEON_AUTH_URL`) repeatedly
leaks into builds despite unsetting it, and the project has permanently
switched to local email/password auth, **remove the provider code path
entirely** rather than managing env vars each build.

### Steps

1. **`lib/auth.ts`**: Remove provider SDK imports (`createInternalNeonAuth`,
   `BetterAuthReactAdapter`), remove the `VITE_NEON_AUTH_URL` env lookup, and
   remove the `configuredAuth` conditional block. Hardcode
   `isNeonAuthConfigured = false`. Export the local auth client directly.
2. **`AuthPage.tsx`**: Remove the `AuthView` import and the
   `isNeonAuthConfigured ? <AuthView> : <form>` conditional — always render
   the local email/password form.
3. **Tests**: Remove the `@neondatabase/auth-ui` mock. Change
   `isNeonAuthConfigured: true` to `false` in the auth mock. Update tests that
   asserted `AuthView` rendering to assert local form elements instead (email
   input, password input, submit button, "Sign in with email" text).
4. Leave `isNeonAuthConfigured` exported as `false` so any code importing it
   still compiles. Add a `ponytail:` comment naming the ceiling and upgrade
   path (restore imports + env gate to re-enable).

### Verification After Permanent Fix

```bash
# Type-check
npx tsc -b --noEmit

# Run focused auth tests
npx vitest run src/__tests__/AuthPage.test.tsx

# Build, deploy, and verify zero Neon markers in deployed bundle
npm run build
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/
JS=$(curl -sS http://<host>/projects/komuna/ | grep -o 'assets/index-[^"]*\.js' | head -1)
curl -sS "http://<host>/projects/komuna/$JS" -o /tmp/bundle.js
grep -c 'neon.tech' /tmp/bundle.js           # must be 0
grep -o 'Sign in with email' /tmp/bundle.js  # must be present
```

## Verification After Deploy

```bash
# Fetch the deployed bundle name from public index
JS=$(curl -sS http://<host>/projects/komuna/ | grep -o 'assets/index-[^" ]*\.js' | head -1)

# Download and check markers
curl -sS "http://<host>/projects/komuna/$JS" -o /tmp/komuna-bundle.js

# Should be 0 — Neon URL must NOT be inlined
grep -c 'neon.tech' /tmp/komuna-bundle.js

# Should be present — local email/password form is the active path
grep -o 'Sign in with email' /tmp/komuna-bundle.js | head -1
```

## Related

- `references/vite-deployed-env-triage.md` — general Vite env-missing-after-deploy triage.
- `references/spa-auth-provider-env-and-fallbacks.md` — auth provider/fallback selection checklist.
- Memory: Komuna login should use basic SQLite/local email-password flow by default, not Neon Auth or Google OAuth.
