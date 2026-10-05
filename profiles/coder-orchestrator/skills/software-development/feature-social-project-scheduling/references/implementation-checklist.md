# Implementation checklist

## Environment inventory

Core: `ADDR`, `DATABASE_PATH`, `MEDIA_DIR`, `PUBLIC_BASE_URL`, `FRONTEND_BASE_URL`, `FRONTEND_URL`, `ALLOWED_ORIGIN`.
Instagram/Meta: `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`, `INSTAGRAM_CONNECT_REDIRECT_URI`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `FACEBOOK_REDIRECT_URI`, `FACEBOOK_LOGIN_CONFIG_ID`, `META_APP_ID`, `META_APP_SECRET`, `META_GRAPH_VERSION`.
Threads: `THREADS_APP_ID`, `THREADS_APP_SECRET`, `THREADS_REDIRECT_URI`.
Auth: `OAUTH_STATE_SECRET`, `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_JWKS_URL`, `AUTH_TOKEN_PEPPER`.
Generation: `SOCIALZEN_GENERATION_MODE`, `SOCIALZEN_GENERATION_URL`, `SOCIALZEN_GENERATION_KEY`, `APP_ENV`.
Frontend-public: `VITE_API_URL`, `VITE_BASE`, `VITE_GOOGLE_CLIENT_ID`, `VITE_POSTHOG_KEY`, `VITE_POSTHOG_HOST`.

Consolidate aliases when starting new systems. Never expose provider secrets in config/status responses.

## Schedule API

Canonicalize and hash the complete schedule payload. Within one transaction: load ownership, replay matching prior keys, reject mismatched hashes, validate 1–50 unique drafts and future RFC3339 times, freeze content/media/targets, create runs/target rows, and persist the response.

## Publisher

Run once at startup and every minute. Claim at most 50 due runs, transition to publishing conditionally, and skip completed targets on restart. Give each destination a stable idempotency key. Record every attempt and classify errors as retryable/terminal. Derive parent status from target rows.

## SQLite

Use WAL, busy timeout, foreign keys, and a single connection when using modernc SQLite. Fully read and close cursors before writes. Enforce immutable snapshots/history and ownership at the DB layer where practical.

## Media

Align browser/server limits; inspect MIME signatures; validate platform dimensions/duration; store generated names under a user directory; write temp then atomic rename; check DB ownership before attachment; clean and confine static paths below `MEDIA_DIR`.

## Tests

Cover request replay/conflict, immutable snapshots, worker restart, partial success, provider/local ID distinction, published-post locking, destination synchronization of drafts only, media traversal/signature/ownership, and legacy migration integrity.
