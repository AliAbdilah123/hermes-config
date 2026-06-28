# Full-stack auth location map lookup

Use when the user asks where a login/auth integration lives in an existing full-stack project.

## Fast lookup pattern

1. Find auth files first: `*auth*`, then search for provider/client keywords (`AuthView`, `createInternalNeonAuth`, `signIn`, `sign-up`, `JWKS`, `NEON_AUTH_BASE_URL`, etc.).
2. Map the flow in layers, not just one file:
   - Frontend route registration (`App.tsx`, router config, links/redirect helpers).
   - Auth page/component that renders provider UI or local fallback form.
   - Auth client/provider setup and env var gate.
   - Backend auth middleware/session/token verification.
   - Env examples/docs and public path/nginx/base-path config if the user asks where to open it.
3. Answer with exact absolute paths and line references, grouped by layer. Mention public URL only if it is derivable from project config/memory.
4. Avoid printing secret env values. Use `.env.example`, docs, config loaders, and key names only.

## Komuna Neon Auth example from session

Project path: `/home/ubuntu/projects/komuna`.

- Frontend routes: `apps/web/src/App.tsx` registers `/auth/sign-in` and `/auth/sign-up`.
- Auth page: `apps/web/src/pages/AuthPage.tsx` renders Neon UI with `<AuthView pathname={pathname} />` when `isNeonAuthConfigured` is true, otherwise falls back to the first-party email/password form.
- Client setup: `apps/web/src/lib/auth.ts` reads `VITE_NEON_AUTH_URL`, creates `createInternalNeonAuth(..., { adapter: BetterAuthReactAdapter() })`, and exports `authClient`/`getJWTToken`.
- Redirect helper: `apps/web/src/lib/authRedirect.ts` builds `/auth/sign-in?redirectTo=...`.
- Backend JWT verification: `apps/api/src/middleware/auth.ts` validates Bearer tokens with `NEON_AUTH_BASE_URL`, JWKS (`/.well-known/jwks.json`), issuer origin, and EdDSA.
- Env example: `apps/web/.env.example` documents `VITE_NEON_AUTH_URL`; API `wrangler.toml`/docs mention `NEON_AUTH_BASE_URL`.
- Public URL shape for the current Komuna deployment: `/projects/komuna/auth/sign-in`.