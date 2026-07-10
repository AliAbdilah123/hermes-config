# Product custom fields and voucher claim answers

Use this when asked what the Komuna spec means by product/voucher custom fields.

## Spec source

`komuna-community-session-bookings.md` §5.6 says:

- Each product may define custom fields.
- v1 supports text fields only.
- Fields are collected at claim time.
- Required/optional is configurable per field.
- The last answer is saved per member and pre-fills the next claim.
- Admins and managers of the product can see answers.

## Schema mapping

Custom field definitions are not arbitrary columns on `products` or `vouchers`.

Definitions live in `custom_fields`:

- `id`
- `product_id`
- `name`
- `required`

Member answers are claim-time data and belong to voucher claims, not directly to vouchers. Answers live in `custom_field_answers`:

- `id`
- `claim_id`
- `field_id`
- `answer`

## Answer shape for future questions

When asked "what are the custom fields in products/vouchers?", answer directly:

- Product custom fields are separate `custom_fields` rows: name + required flag, tied to product.
- Voucher custom field answers are collected when a voucher is claimed/booked/redeemed.
- Answers are stored against `voucher_claims` via `custom_field_answers`, not on `vouchers`.
- v1 field type is text only.

Avoid implying there is a JSON/custom-fields column on `products` or `vouchers`; the model is normalized.