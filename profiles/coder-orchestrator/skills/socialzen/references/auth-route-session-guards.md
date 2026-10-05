# Auth route session guards

Use this pattern when authenticated users can still open login/signup, or guests can open app functionality.

## Route contracts

- Wrap the authenticated application at one shared route boundary. While session state is pending, render a neutral loading state. If no session exists, redirect to `/login?from=<encoded pathname+search>` with `replace`; after login, consume `from` so deep links survive.
- Wrap `/login` and `/signup` in one shared public-only guard. While session state is pending, render loading rather than flashing the form. If a session exists, redirect directly to `/app/dashboard` with `replace`.
- Keep verification, password reset, account restoration, and similar recovery routes outside the public-only guard unless product policy explicitly says active sessions must not access them.
- A frontend guard is navigation UX, not authorization. Backend endpoints must still enforce authentication/authorization.

## Minimal React Router shape

```tsx
function PublicOnlyRoute({ children }: { children: React.ReactNode }) {
  const { data: session, isPending } = authClient.useSession()
  if (isPending) return <PageFallback />
  return session ? <Navigate to="/app/dashboard" replace /> : children
}
```

Reuse the existing session hook and loading component. Do not add another auth-state abstraction for this behavior.

## Regression checks

1. Write a route-level test first: an active session at `/login` lands at `/app/dashboard`, and the login form is absent.
2. Preserve existing protected-route tests for guest redirect and verified/unverified sessions.
3. Run the actual focused runner directly when a package script forwards arguments poorly: `pnpm exec vitest run src/auth-verification.test.tsx`. A script shaped as `vitest run -- <file>` may unexpectedly execute the whole suite.
4. Run frontend typecheck and production build.
5. After deployment, fetch the domain's current HTML, extract its hashed entry asset, and verify that exact public asset returns `Content-Type: application/javascript`. Do not assume an older subpath deployment URL still represents the active domain routing.
