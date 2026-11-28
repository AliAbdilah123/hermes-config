# Membership sponsor modeling

Use this pattern when one party pays dues for another person's membership, including employers paying employee memberships and landlords paying resident memberships.

## Domain separation

Keep these concepts distinct:

- **Beneficiary:** the member whose access, debt, and payment history are affected.
- **Sponsor/payer:** the person or organization responsible for settling the beneficiary's charges.
- **Payment actor:** the account or administrator who records/submits a payment.

Do not anchor sponsorship to a household/unit entity: employer sponsorship proves that the relationship belongs to the membership, not one beneficiary grouping.

## Minimal relational shape

- `payers`: group-scoped sponsor record with display name/contact and an optional linked application user.
- Active membership carries nullable `payer_id`; `NULL` means self-paid.
- Generated charges snapshot `payer_id`. Later reassignment must not rewrite historical charges.
- Keep charges per beneficiary. Aggregate sponsor settlement and sponsor statements can group those charge rows later without merging beneficiary ledgers.

A sponsor may be external. Avoid an enum that conflates person/organization with internal/external status; an optional linked `user_id` plus name/contact is usually enough until behavior truly differs.

## Authorization and privacy

- Managers/admins create sponsors and assign them.
- Members may read their own sponsor through the self-membership endpoint.
- Do not leak sponsor contact information through a member directory visible to ordinary members.
- Validate sponsor and member belong to the same group before assignment.

## Additive migration

When the current system keys membership directly by `(group_id,user_id)`, add sponsorship there first rather than prematurely requiring a full membership-history rewrite. Introduce a separate membership-period entity only when leave/rejoin history is being implemented.

Migration order:

1. Create the sponsor table.
2. Add nullable sponsor FK to current memberships.
3. Add nullable sponsor snapshot FK to charges.
4. Keep existing self-paid rows valid through `NULL` defaults.
5. Verify fresh DB and representative legacy upgrade paths.

## Verification

Test-first checks should cover:

- create/list sponsor with management authorization;
- cross-group assignment rejection;
- assignment and clearing to self-pay;
- sponsor snapshot on newly generated charges;
- historical snapshot unchanged after reassignment/clearing;
- member sees own sponsor but cannot manage it;
- ordinary directory readers do not receive sponsor contact data;
- live public E2E creates, assigns, verifies, clears, and removes its fixture.
