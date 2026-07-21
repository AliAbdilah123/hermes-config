# Account & Data Management: Phases 1–4

Use this reference when implementing or auditing SocialZen account deletion/restoration, private data exports, export jobs, import-ready archives, or safe provider disconnection as one coordinated system.

## One state/version boundary

- Coordinate export, deletion, restoration, permanent deletion, and provider disconnection through durable account state plus a version captured by jobs.
- Keep SQLite transactions short. Never hold a transaction while constructing ZIP files, reading media, or calling provider APIs.
- With `SetMaxOpenConns(1)`, collect query results and close `Rows` before nested database work.
- Deletion rejects new exports, cancels queued jobs, requests safe cancellation of processing jobs, and immediately invalidates completed download access.
- Restoration invalidates pending deletion work but never resumes providers, billing, synchronization, or publishing.

## Phase 1 completion audit

Do not treat password-only deletion as complete. Cover both password and Google-only accounts:

- Google re-auth must verify a fresh GIS token server-side and match the stable `sub` already linked to the same canonical user. Matching email is insufficient, and re-auth must not create/link/switch users.
- Require exact `DELETE`, show the concrete UTC-derived deletion date, revoke sessions, block every ordinary login path, stop publishing/sync, deactivate credentials, stop renewal, and record content-free audit metadata.
- Queue post-commit lifecycle notification/email work and reminders near 7 days and 24 hours before deletion.
- Permanent deletion must be idempotent, resumable, and state-guarded before irreversible stages.
- Keep both migration paths synchronized: `db.go` and `internal/models/models.go`.

## Phases 2–3 export contract

- Use durable asynchronous jobs with `QUEUED`, `PROCESSING`, `COMPLETED`, `COMPLETED_WITH_WARNINGS`, `FAILED`, `CANCELED`, and `EXPIRED`.
- Preflight returns normalized filters, user-scoped counts, estimated size/time, estimated part count, unavailable-data warnings, and the stored-data/provider-availability disclosure.
- Filters support all-time or inclusive month range in the configured timezone, owned connected accounts, data categories, content formats, and media file types. Validate ownership at the API boundary.
- Coalesce only identical active requests for the same user; allow distinct requests while the account remains active.
- Support safe cancellation, retry, re-download before expiry, manual archive deletion, expiration cleanup, and deletion of temporary artifacts after failure/cancellation.
- Deliver archives only after recent re-authentication through short-lived authenticated grants. Never expose public archive URLs or trust a request user ID.
- Store archives privately and encrypted at rest. Use non-guessable IDs, rate limits, safe errors, sanitized archive paths, streamed file handling, and hard limits.
- Use ZIP64 when needed. If configured limits require splitting, create ordered independently checksummed parts and make part assembly instructions explicit.
- Emit one deduplicated post-commit notification snapshot for each required transition; never include archive contents or secret download URLs.

## Phase 4 archive contract

The archive should be versioned and deterministic enough for a future importer without implementing that importer:

- `manifest.json` includes `schema_version`, `minimum_import_version`, `generated_by`, normalized filters, structured warnings, part metadata, stable relationships, and a SHA-256 checksum for every file.
- Include a concise validation/import contract and stable IDs/relationship map.
- Keep profile, connected-account metadata, posts by lifecycle, publishing history, analytics, comments, captions, and ordered media in documented paths.
- Explicitly exclude password hashes, sessions, cookies, provider tokens, encryption keys, download grants, and internal secrets.
- Missing media/provider data should produce a valid `COMPLETED_WITH_WARNINGS` archive when the remainder is usable.

## Safe social-account disconnection

- Preflight real counts for drafts, schedules, active work, retained history, analytics/comments, and provider data that will stop refreshing.
- Recommend export without requiring it.
- On confirmation, immediately stop publishing/sync for that exact connection, safely terminate active work, revoke provider authorization where supported, and retain SocialZen history.
- Mark affected posts for reconnect or target editing; reconnect must not auto-publish.
- Apply the same guarded contract to Instagram, Facebook, and Threads rather than routing every provider through an Instagram-shaped path.

## Verification and reporting

1. Run focused Account/Data backend tests, relevant package tests, and `go build ./...`.
2. Run focused frontend tests for Account & Data, exports, disconnect, restore, and login, then typecheck and production build.
3. Attempt full backend/frontend suites separately. If unrelated legacy failures remain, report their exact areas and distinguish them from focused success.
4. Run `gofmt`/format checks and `git diff --check`; inspect the actual diff for secrets, public paths, ownership bypasses, nested SQLite queries, and both migration paths.
5. Do not infer that a delegated implementation is complete from its summary. Verify requirements against code and test output.
6. When the user explicitly forbids commit/deploy until every requirement is verified, leave changes local and state clearly that production is unchanged. Do not present focused success as a globally green suite.
