# Recoverable private-file deletion

Use when a database row owns a private filesystem object and deletion must avoid both orphaned bytes and broken metadata.

## Failure-safe sequence

Do not choose either naive ordering:

- DB row first, then file: filesystem failure leaves untracked private bytes.
- File first, then DB row: database failure leaves metadata pointing to missing bytes.

Use same-filesystem quarantine:

1. Resolve the server-generated storage key beneath the configured private root and reject traversal.
2. Atomically rename the file to a random quarantine name in the same directory/filesystem. Treat a genuinely missing file according to the endpoint contract; do not silently erase metadata unless that policy is explicit.
3. Begin a tenant-scoped database transaction and delete the exact metadata row.
4. Require exactly one affected row. If execution, row-count validation, or commit fails, roll back and atomically rename the quarantined file back to its original path.
5. Only after commit succeeds, remove the quarantined file.
6. If final quarantine cleanup fails, surface/record an operational cleanup failure; the database must not reference missing original bytes.

Keep the restore path small and explicit. If restoring fails, return a compound error containing both the database and restore failures so operators know manual recovery is required.

## Required regression tests

- Force metadata DELETE failure with a database trigger; assert HTTP failure, metadata still exists, and original bytes/checksum are restored.
- Verify tenant and parent-resource predicates are present in both lookup and DELETE.
- Verify filesystem rename failure does not delete metadata.
- Verify normal deletion removes both metadata and bytes.
- Verify traversal or malformed storage keys are rejected before rename.

Run these focused tests before the full suite. An independent reviewer should inspect failure ordering, not merely accept passing happy-path tests.

## Authenticated SPA E2E after file-lifecycle changes

A valid API session cookie may not enter the authenticated SPA if the client bootstraps auth from local storage. Inspect the frontend contract and seed both the real cookie (through authentication APIs) and required client state such as a CSRF local-storage key before reload. For persistence checks, navigate back to the feature route after reload before locating route-local controls; many SPAs intentionally return to a default route.
