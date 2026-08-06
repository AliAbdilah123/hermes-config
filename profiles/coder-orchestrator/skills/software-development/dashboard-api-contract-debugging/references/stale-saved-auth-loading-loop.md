# Stale saved auth causes an infinite SPA loading screen

## Symptom

On first navigation, the SPA shows a workspace/bootstrap loader forever. Login and registration never appear. The API and static assets may both be healthy.

## Root-cause pattern

1. Auth state is initialized as authenticated from any non-empty persisted token.
2. Auth-derived workspace/onboarding state starts as `null`, which selects the loader.
3. The startup `/me` or session-restoration request rejects because the token is expired or invalid.
4. The error handler records/logs the failure but leaves the persisted token and authenticated state intact.
5. Rendering remains trapped on the loader.

## Minimal fix

Put cleanup at the saved-session restoration boundary. If the authoritative startup auth request fails, remove the persisted credential and clear account, tenant/workspace, and onboarding/session-derived state. The existing unauthenticated branch can then render Login/Register.

Do not apply this cleanup indiscriminately to every dashboard request. A failure in a secondary summary/list endpoint should show a scoped error or retry state, not destroy a valid session.

A small testable helper can wrap only the authoritative restore call:

```ts
export async function restoreSavedSession<T>(fetchAuth: () => Promise<T>, clearAuth: () => void) {
  try {
    return await fetchAuth()
  } catch (error) {
    clearAuth()
    throw error
  }
}
```

## Verification

1. Unit test: make `fetchAuth` reject; assert cleanup runs exactly once and the error propagates.
2. Build/typecheck the final frontend.
3. Public browser E2E: seed a deliberately invalid token before navigation.
4. Assert Login/Register is visible, loading copy is absent, persisted auth is now absent, and no uncaught page error occurred.
5. Also verify a real valid session still reaches its intended dashboard/onboarding destination when credentials are available.

HTTP 200, a healthy `/healthz`, or a fresh asset hash does not prove recovery from stale browser state; the browser must begin with the invalid persisted credential.
