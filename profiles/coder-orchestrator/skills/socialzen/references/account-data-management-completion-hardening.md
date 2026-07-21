# Account & Data Management Completion Hardening

Use this after Phases 1–4 exist but a revised-PRD audit identifies remaining implementation gaps.

## Completion sequence

1. Preserve the dirty worktree. Record baseline status and baseline full-suite failures before changing code; never reset or clean unrelated work.
2. Audit the PRD semantically, row by row. Maintain an evidence matrix mapping each requirement to code and a focused test. A delegated summary is not evidence.
3. Use focused RED/GREEN tests for each remaining behavior, then rerun focused suites, builds, formatting, and full suites.
4. If the user forbids commit/deploy until every requirement is verified, leave all changes local. Do not commit merely because focused checks pass.

## Required hardening checks

- **Provider revocation:** use the provider-specific authorization revocation endpoint. Instagram must not be routed through a Facebook-shaped Graph revocation path; Facebook and Threads retain their own provider paths.
- **Provider export enrichment:** distinguish stored SocialZen data from live provider enrichment. Provider failures should leave a usable archive as `COMPLETED_WITH_WARNINGS` when possible, with structured warning code/provider/object/details/retryability visible in preflight, manifest, history/detail, and notifications.
- **Workspace ownership:** first prove a workspace domain actually exists. If there are no workspace tables, ownership semantics, or transfer API, remove dormant zero-valued ownership fields, transfer guards, and UI claims rather than inventing a speculative subsystem.
- **Export encryption:** archive encryption uses a dedicated required versioned keyring, never `AUTH_TOKEN_PEPPER`. Persist format/key ID with encrypted parts and retain old keys for rotation-compatible downloads. Token pepper may still protect download-grant tokens.
- **ZIP64 and multipart:** plan for total size, single-entry size, and entry-count limits. Generate/split based on the completed archive, then ensure `planned_part_count`, ordered names, sizes, and checksums exactly match actual output. Avoid claiming real >4 GiB validation when tests only exercise a planner; label planner and archive-level evidence separately.
- **Cancellation:** checkpoint before collection, between datasets, during media copy, checksum/encryption chunks, archive creation/splitting, and before final commit. Remove temporary and final artifacts on cancellation/failure.
- **Lifecycle delivery:** disabled email is durably `SKIPPED`; transient send failure is `RETRYABLE`, never silently delivered. Permanent-deletion delivery needs a deletion-safe outbox snapshot so recipient/routing data survives long enough without recreating deleted in-app records.
- **Retry Export:** accept edited filters, normalize and validate them again, enforce canonical connection ownership, fingerprint the edited request, and have the frontend submit the current preflighted filters.
- **Google re-auth:** preserve safe backend error codes and distinguish invalid, expired, and canonical-account mismatch; frontend copy should map codes instead of collapsing everything into a password-oriented error.
- **Import-ready archive:** include stable relationship IDs, unresolved-link warnings, path/filename sanitization, traversal/ZIP-bomb/limit validation contract, schema/minimum-import versions, and SHA-256 for every non-manifest file. Document why the manifest cannot checksum itself.
- **Policy behavior:** resolve retention, renewal/pending-invoice, refund/credit, anonymization, and legal-record behavior explicitly and conservatively in API disclosure and tests. Do not imply an internal legal-record system when obligations remain at the payment processor.

## Verification gate

Run, separately:

- focused Account/Data backend tests;
- `go test ./...` and `go build ./...`;
- focused Account/Data frontend tests;
- full frontend tests, typecheck, and production build;
- `gofmt` on touched Go files and `git diff --check`.

Report pre-existing unrelated full-suite failures separately. Focused green checks prove the feature slice, but they do not justify saying the whole repository is globally green. Do not deploy or commit until the user's stated gate is met.

## Coding-agent model fallback

When a requested low Codex model identifier is rejected, do not stop the task or infer Codex is unavailable. Retry with the CLI's currently configured supported model, keep the requested lower reasoning effort where supported, and preserve the original safety/TDD prompt. The durable lesson is model-name fallback, not the transient unsupported identifier.
