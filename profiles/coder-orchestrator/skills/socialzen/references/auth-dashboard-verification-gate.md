# Auth dashboard verification gate

Use when SocialZen must block unverified email/password users from authenticated app routes while accepting verified Google identities.

## Product rules

- Email/password signup may create a session so the user can resend/check verification, but `email_verified=0` must not permit `/app/*` access.
- Put the frontend gate at the shared protected-route/session boundary, not separately on each dashboard page.
- Redirect unverified sessions to a public `/auth/verification-required` route outside the protected route tree to avoid loops.
- The verification-required page should offer resend, refresh/check status, and sign out.
- After refresh, navigate to `/app` only when the refreshed session explicitly reports `emailVerified=true`.
- Distinguish a refresh/network failure from a confirmed unverified response; do not label every failure “not verified.”
- Keep sensitive backend action gates (`EMAIL_NOT_VERIFIED`) even with the global frontend route gate. Frontend routing is UX, not the security boundary.

## Google verification

- A Google ID token is sufficient only after backend signature/issuer/audience/expiry validation and `email_verified=true` claim validation.
- Do not send a redundant SocialZen verification email to a valid Google account.
- In `findOrCreateGoogleUser`, preserve subject-first identity and conflict checks.
- After all conflict checks pass, update the canonical `users.email_verified=1` for **both** branches:
  1. a new Google identity linked to an existing password user;
  2. an already-existing Google subject identity whose canonical row is stale/unverified.
- Perform the canonical verification update in the same transaction as identity linking/metadata updates.

## Forgot-password behavior

- Keep the public endpoint enumeration-safe: the same success status/shape for existing password users, unknown users, and Google-only users.
- Do not issue a reset token for a Google-only user with an empty password hash.
- Frontend success copy must be conditional in wording, not in response behavior: “If an account with a password exists…” and direct Google users to Continue with Google.
- Test the submitted success state, not only initial explanatory text.

## Email URL configuration

For the subpath deployment, `APP_BASE_URL` must include the complete SPA mount:

```text
https://socialzen.ahsanworks.com/projects/socialzen
```

Generated links should resolve to `/projects/socialzen/auth/verify-email?...` and `/projects/socialzen/auth/reset-password?...`. Resend is transport only; token lifecycle, verification state, and access policy remain backend responsibilities.

## Regression coverage

Backend tests should cover:

- new verified Google identity linking upgrades an existing unverified canonical user;
- existing Google subject identity upgrades a stale unverified canonical user;
- identity/email conflict paths still reject unsafe merges;
- Google-only forgot-password creates no reset token and returns the generic response.

Frontend tests should render real route boundaries and cover:

- unverified session at `/app` redirects to verification-required;
- verified session renders protected content;
- refresh verified → `/app`;
- refresh confirmed unverified → stays with verification copy;
- refresh failure → distinct retryable error;
- forgot-password form submission renders generic conditional copy plus Google guidance.

A helper-only boolean test is insufficient for the primary route-gating requirement.

## Deployment verification

- Run focused backend auth tests, focused frontend route/page tests, typecheck, frontend build, and backend build.
- Restart the backend after correcting the environment and deploy the new frontend bundle.
- Verify service health, the public verification-required route, and the lazy verification chunk returning `application/javascript` with a distinctive copy marker.
- Smoke forgot-password only with a guaranteed unknown address to avoid sending real mail.
