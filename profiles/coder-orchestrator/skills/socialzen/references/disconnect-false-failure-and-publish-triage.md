# Disconnect False-Failure and Publish Triage

Use when a user reports that Facebook/Instagram disconnect failed and publishing/upload also failed.

## Separate the operations

Treat these as distinct boundaries until evidence proves otherwise:

1. Browser media upload (which may happen before any draft exists)
2. Draft/project creation
3. Publishing-target creation and queueing
4. Provider publishing attempt
5. Local disconnect transaction
6. Provider credential revocation
7. Frontend interpretation of the disconnect response
8. Shared mutation guards such as Origin/CSRF validation

A failed upload can leave no `posts` or `post_targets` row at all. An archived/draft project with no targets never reached Meta and is not evidence of a Facebook or Instagram publishing rejection. Start from the exact timestamp, public hostname, route, HTTP method, and status of the user's reported attempt; older successful operations for the same account are context, not proof that the current attempt worked.

## Read-only evidence sequence

1. Identify the exact public URL/device and approximate attempt time. Search access logs for that route/time before interpreting historical database state.
2. Identify the running service's real database path from systemd and process/runtime configuration. Do not assume the repository database is production.
3. Find the user/session without exposing full email addresses or tokens. If similarly named users exist, correlate using the request/session and response size/code rather than choosing by name or old activity.
4. Inspect social account rows: provider, local account ID, current status, token expiry, and whether a token exists. Current `ACTIVE` state can coexist with older completed disconnect operations after reconnection.
5. Inspect recent `connection_disconnection_operations`, revocation audits, and notification timestamps, but match them to the reported attempt time.
6. Inspect recent posts and per-platform targets only if draft creation occurred. For pre-draft failures, inspect the media-upload request and response directly.
7. Correlate access-log method/path/status/referrer with journal entries and frontend error handling. Response byte length can distinguish compact JSON errors when access logs omit bodies; confirm against exact serialization before concluding.
8. When several authenticated mutations from one public hostname all return the same 403 while GETs succeed, inspect the shared Origin/CSRF guard and reverse-proxy `Host`/`X-Forwarded-*` handling before debugging each feature separately.

### Origin/CSRF signature

A deployed alternate hostname can load account data successfully yet reject uploads, disconnects, project creation, and admin writes. The characteristic pattern is:

- authenticated `GET` requests return 200;
- cookie-authenticated `POST`/`DELETE` requests return identical 403 responses such as `FORBIDDEN_ORIGIN`;
- the browser `Origin`/referrer uses an alternate public hostname;
- the backend compares against a configured frontend origin or an internal/upstream `Host` because the proxy did not preserve/interpret the external host.

Fix the canonical external-origin/proxy contract, not each endpoint and never by disabling CSRF checks. Add an authenticated public-host regression covering at least media upload and disconnect.

## Important interpretation

A disconnect can be committed locally before the HTTP response completes. If provider credential revocation runs synchronously afterward, latency, timeout, or a lost response can make the UI show a generic failure even though the database records `COMPLETED` and the account is already disconnected.

Evidence hierarchy:

- Completed disconnect operation + disconnected account row = local disconnect succeeded.
- Provider-revocation audit failure = authorization cleanup failed; it does not roll back the local disconnect.
- `post_targets.status=PUBLISHED` with provider post ID = provider-confirmed publishing success.
- No target row / attempt = failure occurred before provider publishing.

## Minimal fix shape

- Keep the local disconnect transaction idempotent.
- Do not hold the user-facing response open for best-effort provider revocation; move revocation to a durable outbox/background operation when practical.
- After an ambiguous frontend error, refetch authoritative account state before declaring failure.
- Preserve and display the actual API error code/message instead of replacing every exception with one generic sentence.
- Add tests for: committed disconnect plus delayed/failed revocation; repeated disconnect; and frontend reconciliation after an ambiguous response.

## Reporting

State exact timestamps, provider, target status, whether provider processing ran, and the recorded error. Never expose access tokens. Do not claim that “upload failed at Meta” when no provider target or attempt exists.
