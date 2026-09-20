# Social Provider Token Topology and Generic Error Triage

Use when account lookup fails through a social-provider API and the UI shows a generic request error.

## Separate credential contracts

A token valid for one API topology is not automatically valid for another endpoint on the same platform. Keep these contracts distinct:

- Instagram Login / Instagram User access tokens used with `graph.instagram.com`.
- Facebook Login / Page access tokens and connected professional-account IDs used with Facebook Graph Business Discovery.

Do not reuse one env variable for both merely because both concern Instagram. Name credentials by topology and purpose.

## Evidence sequence

1. Capture the browser request path, HTTP status, content type, and response body.
2. Verify reverse-proxy rewriting separately from provider failure.
3. Inspect the exact upstream host, API version, account-ID role, and token variable used by the backend.
4. Reproduce the provider request read-only with secrets masked. Retain only sanitized provider fields: HTTP status, error type, code, and subcode.
5. Inspect token metadata without printing it: presence, length, prefix family, quoting, and whitespace.
6. Compare the credential topology with authoritative provider requirements and the product's documented auth architecture.
7. Inspect the deployed frontend bundle's error-code map, not only source.

## Report two layers separately

- **Operational root cause:** why the provider rejected the request, such as an incompatible token topology.
- **Presentation failure:** why the UI displayed generic copy rather than the backend's mapped error.

If the backend is proven to return a recognized JSON error but the user saw generic text, do not claim that response produced the wording. Generic fallbacks generally require non-JSON, an empty body, or an unknown code. Historical logs without response bodies cannot distinguish those cases; obtain an authenticated browser HAR or reproduce in-browser.

## Product/config consistency

Do not advertise search capability unconditionally. Derive `search_enabled` from credentials specifically required for that search topology. A broad feature flag that is validated but ignored by handlers is not an effective gate.

## Minimal fixes

Choose one architecture:

- Add separate Business Discovery credentials while retaining Instagram Login credentials for messaging; or
- If the product intentionally remains Instagram-Login-only, replace arbitrary discovery with **connected-account validation** through the Instagram Login API.

For the Instagram-Login-only path:

1. Call `GET https://graph.instagram.com/<configured-version>/me?fields=id,username,name,profile_picture_url` with the existing Instagram User token in `Authorization: Bearer <token>`.
2. Normalize the requested username and provider-returned username identically.
3. Return the `/me` account only on an exact normalized match; return an empty result for every other username. Do not imply that Instagram Login supports arbitrary public username discovery.
4. Revalidate the same `/me` account ID when the user confirms connection, before creating the pending identity.
5. Derive `search_enabled` from availability of the Instagram User token, not a Facebook Page/account ID or an unrelated broad feature flag.
6. Keep dedicated account IDs that are still needed for webhook/message routing, but never include them in the `/me` lookup.

Use the configured Graph version rather than scattering a literal. Prefer bearer authorization so tokens do not appear in URLs or proxy logs. Parse provider error JSON only far enough to classify sanitized fields such as OAuth `code=190`; never return or log the token, provider message, trace ID, or raw body. Map authentication, unconfigured lookup, and temporary provider failures to stable application error codes with explicit frontend copy, so expected provider failures never fall through to a generic unknown-error message.

## Search UI state contract

A technically correct connected-account endpoint can still look broken when an empty `accounts: []` response renders nothing. Treat search as an explicit state machine rather than deriving all feedback from the result array:

- Track in-flight and completed-success states separately from matches and errors.
- On submit, trim/validate the username, reject duplicate submission while in flight, clear stale results, then set loading before awaiting.
- While loading, disable submit, show `Searching…`, and expose `role="status"` with `aria-live="polite"`.
- A successful empty result must show that no matching **connected** account was found and that the username must match the account connected to the app.
- A match preserves profile review and ownership confirmation. A failure uses `role="alert"`; never show no-result guidance over an error.
- Clear stale result/no-result state when input changes, the flow is cancelled, or the user starts again.
- Discard async completion when the platform was cancelled or the current trimmed username differs from the submitted query.

## Verification matrix for connected-account lookup

- Provider-contract test: exact host `graph.instagram.com`, configured version, `/me` path, expected fields, bearer token, and absence of `graph.facebook.com`, `business_discovery`, account IDs, and query-string tokens.
- Behavioral tests: case/`@` normalization match returns one account; mismatch returns `accounts: []`; confirmation rejects changed ID/username; token absence disables search.
- UI-state tests: duplicate-submit prevention, accessible pending state, explicit empty-success guidance, visible API errors, stale-response suppression, and reset on input/cancel.
- Failure tests: OAuth JSON and non-JSON provider failures produce stable sanitized application errors without leaking raw provider data.
- Live preflight: make a read-only `/me` request with the effective runtime token and retain only status, username, and ID presence.
- Authenticated public E2E: hold one request to prove loading/disabled behavior; use a valid-length nonmatching username to prove empty-result guidance; type again to prove stale guidance clears; then search the connected username and require HTTP 200, exact username, and confirmation. Invalid usernames test validation, not no-match behavior.
- Require no unexpected console/page/request failures, clean up disposable users, and run SQLite `PRAGMA integrity_check` after E2E.

A common browser-harness trap on subpath deployments is matching `/dashboard|notes/` against the application base path itself (for example `/projects/social-notes/`). Assert the exact pathname (`/projects/social-notes/dashboard`) before navigating to authenticated Settings; otherwise an unauthenticated redirect can be misdiagnosed as a missing search control.
