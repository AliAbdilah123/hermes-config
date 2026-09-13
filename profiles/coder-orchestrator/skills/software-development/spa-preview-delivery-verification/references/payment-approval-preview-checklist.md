# Payment Approval Preview Checklist

For SPA previews involving SQLite-backed manual payment approval:

- Run focused feature tests first. Reproduce any full-suite failure against a clean worktree at the same baseline before changing unrelated code; report feature and baseline failures separately.
- Avoid nested `database/sql` queries while an outer `Rows` cursor is open. Materialize and close the outer rows first, then enrich them. Add a bounded `SetMaxOpenConns(1)` regression.
- Recheck mutable payment-method flags inside the purchase transaction.
- Require resubmitted package/session intent to match the original purchase.
- Verify no entitlement before approval and exactly one entitlement/notification after duplicate approval attempts.
- Fetch protected receipt images through the authenticated API client, render a blob URL, and revoke it on close/unmount. Plain `<img src>` requests cannot attach bearer tokens.
- Reorder positioned records atomically; changing only one row can create duplicate positions.
- Public E2E must cover both roles: program admin configures bank details; member uploads a valid receipt; admin views it through the protected endpoint and approves/rejects; member sees pending/approved status and notification.
- Use an isolated SQLite backup/API and prove production assets and data are unchanged.
