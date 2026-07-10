# Purchase history must include package items

## Trigger

Use this when a Komuna profile/member purchase history page shows paid purchases with `0 items`, blank package names, or wrong item counts even though checkout/payment succeeded.

## Root cause pattern

The database may be correct while the API response is wrong. In the Go+SQLite API, purchases are stored in `purchases`, package links in `purchase_items`, and package labels in `purchase_packages`. A profile page that renders `purchase.items.length` and `purchase.items[].package.name` will show `0 items` if `/api/v1/purchases` returns a hardcoded empty `items: []` from the purchase scanner.

This is not a payment/checkout failure if this query returns item rows:

```bash
sqlite3 sqlite.db "SELECT u.email, pu.id, pu.status, pu.total_amount, COUNT(pi.id), GROUP_CONCAT(pp.name) FROM purchases pu JOIN program_members pm ON pm.id=pu.program_member_id JOIN auth_users u ON u.id=pm.user_id LEFT JOIN purchase_items pi ON pi.purchase_id=pu.id LEFT JOIN purchase_packages pp ON pp.id=pi.package_id WHERE u.email='<email>' GROUP BY pu.id;"
```

## Minimal fix shape

- Keep `scanPurchase` as the scalar purchase scanner.
- Add one helper that loads `purchase_items` joined to `purchase_packages` for a purchase ID.
- In every purchase-history list endpoint that returns purchase DTOs (`/purchases` and program-scoped purchases), replace the hardcoded empty `items` with the helper result.
- Add/extend a regression test that asserts the purchase history JSON includes one item with `package_id` and a non-empty `package.name` after payment completion.

## Verification

```bash
cd /home/ubuntu/projects/komuna/api/v1
go test . -run 'TestPaidXenditCheckoutAppearsInPurchaseHistory|TestPaidSubscriptionPackageCreatesEntitlementAndClaim' -count=1
go test .
```

After deploy, verify the running API, not only the DB:

```bash
TOKEN=$(sqlite3 -noheader /home/ubuntu/projects/komuna/sqlite.db "SELECT token FROM auth_sessions WHERE user_id=(SELECT id FROM auth_users WHERE email='<email>') AND expires_at > datetime('now') ORDER BY created_at DESC LIMIT 1;")
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8095/api/v1/purchases \
  | python3 -c 'import json,sys; j=json.load(sys.stdin); print([(p["id"], p["status"], len(p["items"]), [i["package"]["name"] for i in p["items"]]) for p in j["data"]])'
```
