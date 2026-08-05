# Existing-module CSV imports

Use this when upgrading or adding CSV-to-database ingestion inside an established backend module.

## Integration reconnaissance

Trace the canonical route, handler/service boundaries, entity insert helpers, normalization and validation, duplicate semantics, audit/import tables, review-queue filters, migrations, logging, authentication, and focused tests. Confirm the real repository path before launching an autonomous coding agent; similarly named directories are common.

Upgrade the existing importer rather than adding a disconnected implementation. A raw-body, `ReadAll` endpoint may need replacement with multipart streaming when the new contract explicitly requires it.

## Behavioral contract

Write endpoint/service regressions first for:

- multipart field, extension, MIME, size, empty-file, and malformed-file handling;
- UTF-8, quoted commas, escaped quotes, CRLF/LF, blank rows;
- case-insensitive and order-independent required headers plus supported aliases;
- row normalization and validation while later rows continue;
- O(n) duplicate handling against persisted data and prior rows;
- configurable batch transactions and failed-batch rollback boundaries;
- Import Batch creation and successful entity linkage;
- structured totals and row-level error payloads;
- contact creation only when contact data exists;
- exact lifecycle/source defaults and visibility through the existing review queue;
- absence of unintended adjacent entities such as prospects, CRM records, opportunities, or leads.

Keep the requested domain entity canonical. Reuse established tenant/auth, insertion, contact, validation, and migration abstractions. Add schema only where audit/linkage requires it, then verify existing-database upgrade and clean bootstrap.

## Scale and safety

Stream rows and retain only the current configurable batch plus bounded reporting state. Use hash keys for in-file duplicate checks, parameterized SQL, and one transaction per batch. Inspect pre-existing dirty/untracked files before delegation and exclude them from agent scope, staging, and commits.
