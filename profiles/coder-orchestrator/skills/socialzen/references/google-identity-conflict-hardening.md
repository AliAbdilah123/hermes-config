# Google Identity Conflict Hardening

Use when changing SocialZen Google Sign-In or `user_identities` linking logic.

## Problem shape

Google login must treat the stable Google `sub` as primary identity and verified email as a linking hint only. Two conflict paths must return an explicit user-safe error instead of merging accounts:

1. A new Google `sub` arrives with an email already present on an existing Google identity with a different `provider_subject`.
2. An existing Google `sub` returns a changed email that belongs to a different canonical `users.id`.

Return `409 ACCOUNT_LINK_CONFLICT` with actionable copy. Do not silently update the identity email or create/link a second identity in those cases.

## Minimal implementation pattern

- In `findOrCreateGoogleUser()`, normalize verified email once: `strings.ToLower(strings.TrimSpace(c.Email))`.
- Lookup by `(provider='google', provider_subject=sub)` first.
- If no subject identity exists, check for any Google identity with the same email and a different subject before linking by `users.email`.
- If subject identity exists, check whether the returned email belongs to another `users.id` before updating identity metadata.
- Surface `errAccountLinkConflict` from the helper and map it in `signinGoogle()` to `409 ACCOUNT_LINK_CONFLICT`.
- Frontend `signInWithGoogle()` should preserve `error.code` from `authClient.signIn.google()` so Login/Signup can show conflict-specific copy.

## Regression tests

Add focused backend tests for:

- existing Google email + different subject → `409 ACCOUNT_LINK_CONFLICT`
- existing subject + email owned by another user → `409 ACCOUNT_LINK_CONFLICT`
- normal new Google user creation still creates a passwordless user + one identity
- verified email linking to an existing password user still works when no Google conflict exists

Targeted command:

```bash
cd apps/backend-go
go test -run 'TestGoogleSignIn|TestPasswordOnlyLoginRejectsGoogleOnlyUser' .
```

Full `go test ./...` can contain unrelated repo failures; report those separately instead of broadening the auth change.
