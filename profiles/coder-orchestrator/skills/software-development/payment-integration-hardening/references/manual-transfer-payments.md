# Manual transfer payment audit checklist

Use for member-uploaded transfer receipts that staff review before fulfillment.

## Authorization and ownership

- Scope bank-account CRUD, submission listing, receipt reads, approval, and rejection by the program derived from the purchase membership—not merely by a route parameter.
- Require program-admin authorization before every administrative branch, including binary receipt responses.
- For creation, require the selected bank account to be active and belong to the purchased package's program.
- For resubmission, scope the purchase to the authenticated buyer and require it to be a manual, rejected, still-pending purchase.

## Receipt handling

- Enforce request and file size limits server-side; do not rely on browser MIME or `accept`.
- Validate a narrow extension, signature/container structure, and decodability. Generate the storage key server-side, use a private non-static directory, restrictive permissions, basename defense, `nosniff`, `no-store`, and a restrictive CSP for inline display.
- A protected `<img src>` cannot attach a bearer token. In bearer-auth SPAs, fetch the receipt through the authenticated API client, convert it to a blob/object URL, and revoke the URL when done. Plain image URLs are acceptable only under an explicitly verified same-origin cookie contract.
- Treat filesystem and database persistence as a distributed transaction. Stage the new file, commit the metadata transition, atomically promote it, and retain enough state for crash recovery/orphan cleanup. Check crash windows both after DB commit and before old-file deletion.
- Stream or serve the file without unnecessary full-memory duplication where practical; preserve the size check against stored metadata.

## Transactions, idempotency, and entitlement timing

- Keep purchase creation, item/snapshot rows, manual submission metadata, and audit insertion in one DB transaction.
- Recheck mutable authorization/configuration facts inside that transaction, including whether manual payments remain enabled and whether the bank account is still active.
- Idempotency must be DB-backed and scoped to the buyer/member. A repeated key must match package, payment method, session intent, and booking answers; otherwise return conflict.
- A resubmission is a receipt replacement, not a new checkout. Reject changed package/session/answers or omit those fields from the resubmission contract. Never silently ignore conflicting intent.
- Approval must atomically transition pending purchase and pending submission, set paid time, create all entitlements, and write notifications/audit. Duplicate or concurrent approvals must issue benefits exactly once.
- Rejection must not mark the purchase paid or issue entitlements. Reapproval of rejected submissions requires a deliberate resubmission transition back to pending.
- Ensure gateway webhook/reconciliation paths cannot finalize `payment_method='manual'` purchases; provider finalizers should assert the expected payment method or invoice identity.

## Frontend/API contract

- Define a narrow public bank-account DTO for checkout options; do not type a partial response as the richer admin DTO.
- Model manual submission state separately from purchase payment state and render rejected/pending/approved combinations explicitly.
- Verify multipart field names, casing, response status, nullable fields, and authentication behavior against the actual backend handler.

## Focused adversarial cases

- Admin from program A attempts list/read/approve/reject against program B.
- Buyer attempts to resubmit another buyer's purchase or changes package/session/answers.
- Manual method or selected account is disabled while upload is in flight.
- Two approvals race; approval races rejection or resubmission.
- Process crashes around staged-file write, DB commit, file promotion, and old-file deletion.
- Receipt is oversized, empty, polyglot, malformed, wrong extension, or valid type with attacker-controlled filename.
- Bearer-auth administrator lists submissions successfully but receipt image retrieval lacks authorization.
