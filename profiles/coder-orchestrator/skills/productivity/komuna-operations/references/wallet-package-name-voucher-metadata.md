# Wallet package-name voucher metadata

When a member reports that wallet vouchers or voucher pockets do not show the purchased package/product label:

## Triage

1. Treat the screenshot as a display symptom, not proof of missing entitlements.
2. Query the member's vouchers and subscriptions with purchase/package joins:

```sql
SELECT v.id voucher_id, v.product_id, p.name product_name, v.purchase_id,
       pp.id package_id, pp.name package_name, v.status, v.expired_at
FROM vouchers v
JOIN program_members pm ON pm.id = v.program_member_id
JOIN users u ON u.id = pm.user_id
JOIN products p ON p.id = v.product_id
LEFT JOIN purchases pu ON pu.id = v.purchase_id
LEFT JOIN purchase_items pi ON pi.purchase_id = pu.id
LEFT JOIN purchase_packages pp ON pp.id = pi.package_id
WHERE lower(u.email) = lower(?);
```

3. Compare what the database knows (`products.name`, `purchase_packages.name`) with what `/wallet` DTOs expose.

## Common root cause

The wallet query/DTO may hydrate vouchers with `products.name` only. If the UI is expected to show a purchased package label such as `Intro 5-Class · Sunrise Vinyasa`, the wallet API must join and expose package metadata; changing only the React component cannot work because the data is absent.

## Minimal fix shape

- Extend the wallet repository query to left join purchase item/package metadata for purchase-backed vouchers.
- Add nullable package metadata to the relevant DTO(s), preserving existing product fields.
- Display pocket/voucher titles with package + product when package name exists, otherwise fall back to product name.
- Add a regression test around the wallet API/DTO contract using a purchase-backed voucher where `package_name` is distinct from `product_name`.

## Pitfall

Do not assume "product name" and "package name" are the same concept in Komuna. Vouchers are scoped to products, but purchases can be of packages that grant multiple product entitlements.