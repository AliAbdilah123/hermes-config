---
name: stateful-collection-frontends
description: Implement and verify frontend collection screens with URL-persisted search/filter state, multi-selection, local export, partial-failure bulk actions, and explicit lazy detail enrichment.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [frontend, collections, url-state, bulk-actions, export, lazy-loading, tdd]
    related_skills: [test-driven-development, code-change-verification]
---
# Stateful Collection Frontends

## Contract

Use for list/detail features that combine search and repeated filters, browser-history restoration, stale-request protection, visible-page selection, local export, destructive actions, or quota-sensitive enrichment. Preserve accessibility and failure state; minimize dependencies and reuse existing API operations.

## TDD sequence

1. **API serialization:** Capture the real `Request`; assert repeated parameters with `URLSearchParams.getAll()`. `Object.fromEntries()` drops duplicate keys.
2. **Pure transformations:** Build export/serialization as a small pure helper. Test deterministic ordering, escaping, optional metadata, and separators before UI wiring.
3. **URL state:** Test mount restoration, forward/back restoration, repeated keys, and canonical URL writing.
4. **Async races:** Use deferred requests to prove older responses cannot replace newer state.
5. **Selection:** Test one row, all visible, and cleanup after paging/filtering/refresh. “All” means visible records unless explicitly specified otherwise.
6. **Destructive actions:** Test one confirmation, sequential requests, partial failure reporting, and retention of only failed selections.
7. **Lazy detail enrichment:** Prove initial render sends zero enrichment/provider requests, then test loading, error, one request per activation, and retry.

Prefer component/browser interaction tests. Source-text assertions are a fallback only when the repository lacks a component harness; keep them semantic and never weaken a test merely to bless requirement drift.

## Implementation rules

- Read state from the URL on mount and history navigation; write repeated filter values with `append()`.
- Protect result assignment with an incrementing request generation or cancellation mechanism.
- Render accessible checkbox groups, visible tags, and individually removable active filters.
- Generate downloads locally with platform `Blob`, object URLs, and a fixed safe filename unless requirements say otherwise.
- Reuse an existing owner-scoped, CSRF-protected single-delete endpoint sequentially before adding a bulk endpoint.
- After destructive partial failure, refresh data and keep only failed IDs selected with a visible error.
- Defer quota-sensitive/provider-backed detail work behind explicit user activation.

## Shared-tree safeguards

Respect assigned file ownership. Inspect scoped status before and after; never clean, revert, or overwrite another agent’s work. Run the repository’s canonical frontend tests, static checks, and production build after the final change.

## Reference

See `references/social-notes-example.md` for a concise worked contract.
