# Payment redirect immediate confirmation

Use when a payment provider (Xendit, Stripe, etc.) redirects the user back to
the app after payment, but the webhook that persists the subscription hasn't
arrived yet — causing a long "Confirming your payment…" spinner that eventually
times out.

## Problem

Typical flow:
1. Backend creates invoice with `success_redirect_url` pointing to a return page.
2. User pays on the provider's hosted checkout.
3. Provider redirects user back to `success_redirect_url?status=SUCCEEDED`.
4. Provider fires a webhook to the backend — but this can lag seconds or never
   arrive (misconfigured webhook URL, network issue, dev environment).
5. Frontend return page polls `/api/subscription/status` waiting for the tier to
   change. If the webhook hasn't landed, it polls until timeout → "payment failed."

## Fix pattern

**Include `externalId` in the success redirect URL and confirm immediately.**

### Backend

1. When creating the invoice, build the `external_id` as a parseable string
   that encodes `user_id` and `plan_id`:
   `socialzen-{userID}-{planID}-{unixTimestamp}`.
2. Append `&externalId={external_id}` to the `success_redirect_url`.
3. Add a `POST /api/subscription/confirm?status=...&externalId=...` endpoint that:
   - Requires an authenticated session (`RequireUser`).
   - Verifies the `externalId` contains the signed-in user's ID (ownership check:
     `strings.Contains(externalID, "-"+u.ID+"-")`).
   - Verifies `status` is a paid status (`PAID`, `SUCCEEDED`, `SETTLED`).
   - Parses `user_id` and `plan_id` from the `external_id` and upserts the
     subscription row immediately.
   - Returns the updated `SubscriptionData` so the frontend gets the new tier
     in the same response.
4. Keep the webhook handler as the source of truth for unpaid→paid transitions
   (it still runs for reliability), but the confirm endpoint provides the
   instant UX path.

### Frontend

1. Return page reads `externalId` from query params.
2. On the **first** poll attempt, calls `POST /api/subscription/confirm` instead
   of `GET /api/subscription/status`.
3. If confirm returns a non-FREE tier → show success immediately, no polling.
4. If confirm fails (e.g. externalId missing from an older invoice), fall back
   to the normal status-polling loop as before.

### Ownership check detail

The confirm endpoint must verify that the `externalId` belongs to the
authenticated user. The `external_id` format uses `-` as a delimiter:
`socialzen-{userID}-{planID}-{timestamp}`. Since user IDs in this project use
`_` (e.g. `user_abc123`), the `-` delimiter is safe. The check
`strings.Contains(externalID, "-"+u.ID+"-")` ensures user A cannot confirm
user B's payment.

## Test

- Unit test `applyPaidExternalID(db, "socialzen-user_123-tier_2-1234567890")`
  activates the subscription row with the correct `plan_id` and `status='active'`.
- Unit test `paidStatus()` accepts `PAID`, `SUCCEEDED`, `SETTLED` and rejects
  `PENDING`.
- Frontend: existing PaymentReturn tests still pass (the confirm call only fires
  when `externalId` is present and on attempt 1).
