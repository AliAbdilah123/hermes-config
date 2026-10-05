---
name: feature-pos-operations
description: Use when implementing POS orders with recipe-aware inventory, open bills, transactional settlement, offline replay, receipt expense ingestion, or menu experiments.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, pos, inventory, offline, receipts]
    related_skills: [feature-xendit-payments, feature-multi-tenant-saas]
---
# Feature: POS Operations

## Workflow
Aggregate recipe requirements for the whole cart; return machine-readable shortages; accept only explicit one-use overrides. Decide whether stock is reserved at order creation or settlement. Settlement, payment record, stock deduction, and movement ledger commit once in one transaction.

Offline clients use stable device/mutation IDs. Server uniqueness replays accepted results and retains conflicts for explicit resolution.

Receipt ingestion bounds multipart bytes, allowlists MIME, verifies magic bytes, persists the original, isolates parser calls, and creates editable line-item drafts. UI ignores stale async results.

Menu experiments snapshot versions, validate bundles/variations before activation, bind sessions to a version, and finalize from persisted observations.

## Configuration
`DATABASE_PATH`/`POS_DB_PATH`, `PORT`, optional `POS_RECEIPT_PARSER_URL`. Provider payments belong to `feature-xendit-payments`.

## Templates
- `templates/pos-schema.sql`
- `references/receipt-ingestion.md`
- `references/verification-cases.md`

## Pitfalls
Settlement-time-only deduction can oversubscribe stock; random/time IDs weaken replay; MIME headers lie; aggregate JSON state causes coarse conflicts; simulated QRIS is not production payment evidence.

## Verification
Concurrent carts, duplicate settlement, override reuse, replay/conflict, parser timeout, stale UI result, signature/size rejection, and transaction rollback.

## Provenance
Core: `fnb-pos`; receipt/menu extensions: `light-pos`. `fnb-pos-system` is empty lineage only.
