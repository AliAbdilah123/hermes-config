# SPA Session Cache Staleness After Auth

## Symptom

User signs in successfully (API returns 200 + user data), but immediately sees "Signed in, but
session not established" or is redirected back to login. The backend logs show no session errors.

## Root Cause

A frontend module-level session cache with a TTL (e.g. 5 minutes) stores `{ data: null }` from
the initial unauthenticated page load. After `signIn()` succeeds and the browser now has the
session cookie, the page calls `getSession()` — but the cache is still fresh, so it returns the
stale `null` instead of making a real HTTP request.

## Detection Pattern

1. Search for `getSession()` calls after `signIn()`/`signUp()` in auth pages.
2. Check whether the session store uses an in-memory cache with TTL.
3. Check whether `signIn` clears or invalidates that cache.
4. If `signIn` doesn't touch the cache: the bug is confirmed.

## Fix

Use a **force-refresh** variant (e.g. `refreshSession()`) after sign-in, not the cached
`getSession()`. The refresh variant must bypass the TTL and make a real request:

```typescript
// Wrong — returns stale null from cache
const { data: session } = await authClient.getSession()

// Right — forces a fresh fetch regardless of TTL
const { data: session } = await authClient.refreshSession()
```

If no refresh variant exists, the simplest option is to expose a `clearSessionCache()` helper
that resets the module-level state, then call `getSession()`.

## Prevention

- `signIn()`/`signUp()` should clear the session cache before returning.
- Or the session cache TTL should be 0 after any auth mutation.
- Tests should mock the real sequence: sign-in → stale cache → force refresh.

## Example (react/ts)

Module-level cache (bad):
```js
const cache = { data: null, fetchedAt: 0 }
const TTL = 5 * 60 * 1000

async function getSession() {
  if (Date.now() - cache.fetchedAt < TTL) return { data: cache.data }
  // ... fetch ...
}

// After signIn(), getSession() returns stale null.
```

Fix — call refresh, not get:
```js
const { data } = await authClient.refreshSession() // always fetches
```
