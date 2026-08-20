# Stale client auth, missing session cookie

## Symptom pattern

Several protected modules fail together with raw `{"error":"unauthorized"}`, but navigation/account chrome still looks authenticated.

## Interpretation

- `unauthorized`: no session cookie reached middleware.
- `session_not_found`: a cookie token arrived but has no session row.
- `bad_session`: cookie format/signature validation failed.

The first case commonly means local storage retained a CSRF/auth marker after the HttpOnly cookie disappeared. Persistent database sessions and an unchanged signing secret do not repair a request that carries no cookie.

## Shared-client fix shape

- Maintain a set of public auth paths that must not trigger recovery.
- For other 401 responses, remove the durable client marker and dispatch one root-level auth-required event.
- Root App subscribes once, clears account/tenant/onboarding state, and renders Login.
- API errors expose `status`, raw `code`, and parsed `data`; the display message for 401 is localized session-expired copy.
- Root bootstrap ignores only the expected API 401 after recovery. It still logs network and server failures.

## Focused regression matrix

1. Stale marker + no cookie on Prospect request → marker removed, event emitted, clean 401 message.
2. Repeat for Offers and CRM to prove shared coverage.
3. Login/register/invitation 401 → marker untouched and no recovery event.
4. 500 and network errors → not classified as expected auth recovery.

## Public browser proof

1. New browser context; seed only stale client marker.
2. Navigate directly to a protected route.
3. Assert Login visible, marker absent, raw JSON absent, and no uncaught page error.
4. Enter real credentials and submit through the public UI.
5. Assert login HTTP 200, fresh marker present, and authenticated navigation visible.

A browser may log the expected 401 as a failed network resource. Record `pageerror` and explicit application error logging separately; do not require the browser networking console to be completely silent during deliberate 401 recovery.
