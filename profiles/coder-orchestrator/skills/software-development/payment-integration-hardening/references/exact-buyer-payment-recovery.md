# Exact-buyer payment recovery

Use when the provider says paid/settled but the user sees confirmation failure or no entitlements.

## Correlate before reconciling

Never pick a purchase because it is recent, familiar, or belongs to an existing test account. Correlate the exact browser checkout to:

- checkout timestamp and request/session evidence;
- emitted purchase ID and provider external ID;
- authenticated user ID, membership ID, and email;
- provider invoice ID, status, and paid timestamp;
- the exact provider-issued return URL the browser opened.

List ambiguous purchases before acting. A successful reconciliation for a different account is a failed recovery.

## Prove the user's outcome

Record baseline purchase status, entitlement count, and claim count for the exact buyer. Reconcile through the same authenticated public URL/API path the user uses. Then verify:

1. provider external ID matches the purchase;
2. the intended environment/database receives confirmation;
3. purchase becomes paid only from provider truth;
4. entitlements belong to the exact buyer membership;
5. intended booking exists exactly once;
6. that buyer's wallet/My Bookings UI visibly shows the result;
7. repeated confirmation does not change counts.

## Old preview return URLs

A code fix changes future invoices, not provider-issued URLs already stored on old invoices. If an old preview invoice targets production, add only a temporary compatibility bridge keyed to the verified purchase ID. Test origin and public edge, including final HTTPS Location, then open the exact old URL in the buyer's authenticated browser. Remove the bridge with the preview.

Do not report success from a manually corrected URL, a seeded token for another user, or database rows that are not visible in the actual buyer's account.
