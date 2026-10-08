# Bulk relational label editing

Use this pattern when users select multiple records and append/remove tags, labels, categories, or similar many-to-many metadata.

## Minimal contract

- Model the mutation explicitly as `{record_ids, add, remove}`. Do not overload a normal full-record update or require one request per record.
- Keep the operation owner/tenant scoped in one database transaction. IDs outside the caller's scope must never be mutated.
- Apply the whole batch transactionally so a mid-operation failure cannot leave a partially edited selection.
- Normalize comparisons (usually case-insensitive), deduplicate requested values, and make append/remove idempotent.
- Bound record count, label count, and label length at the API trust boundary; reject empty mutations and invalid syntax.
- Define overlap semantics when the same normalized label appears in both sets. Prefer rejecting overlap or document deterministic precedence.
- Return `204` when callers only need to refresh, then reload both records and available-label filters.

## UI pattern

- Put **Bulk edit labels/tags** in the existing selected-record actions menu rather than adding a second bulk-action surface.
- Show separate, plainly labeled append and remove inputs. Preserve selection while editing and after validation/server errors.
- Disable submit while saving, expose errors accessibly, and keep the form usable at mobile widths.
- Confirm destructive record deletion, but avoid confirmation friction for reversible metadata edits unless policy requires it.

## Verification

Test append, remove, case-insensitive dedupe, idempotency, mixed ownership, CSRF/auth, empty/oversized/invalid payloads, and rollback behavior. Public E2E should select multiple records, append one label, remove another, reload, and verify all selected records plus an unselected control record.

## Important domain check

If labels are normally derived from record content, decide explicitly whether bulk-added labels are independent metadata or should rewrite source content. Independent relation edits may be overwritten by later content re-analysis; content rewriting changes user-authored text. Never silently choose between these semantics.
