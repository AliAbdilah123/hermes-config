# Pending expiry and invoice resume

Use this checklist when payment attempts remain pending and users need to finish an existing invoice.

## Status semantics

- Preserve `pending`, `paid`, `failed`, `expired`, and `refunded` distinctly across DB constraints/migrations, API DTOs, filters, counts, and UI labels.
- Query provider state during reconciliation. Provider `PENDING` beats an elapsed local deadline when a usable invoice identity exists.
- Map explicit provider `EXPIRED` to local `expired`.
- On provider/network errors, leave status pending and retry.
- A conservative local expiry is acceptable only when there is no usable provider invoice identity and a trustworthy stored provider expiry timestamp has elapsed.

## Scheduler

- Start reconciliation from application startup.
- Run once immediately, then on a configurable bounded interval.
- Use the same canonical, transactional, idempotent finalizer as callbacks.
- Conditional pending-only updates prevent late callbacks from downgrading paid purchases.

## Purchase surfaces

Admin purchase lists should display/filter/count Expired, but must not receive resumable invoice URLs.

Owner purchase history may show:
- “Payment pending” and clear incomplete-payment copy;
- the provider deadline when available;
- “Complete payment” linking to the existing invoice only.

Do not show the action when status is non-pending, URL host/scheme is invalid, or a valid deadline has elapsed. Missing deadlines may retain the action only while backend status remains pending and the URL passes validation.

## Data boundary

Treat invoice URLs as sensitive bearer-like links. Return them only from an authenticated ownership-scoped query such as `WHERE member.user_id = current_user`. Use distinct member/admin DTO types so an admin query cannot accidentally serialize the field.

## Regression tests

1. Provider EXPIRED becomes local expired and no benefits are issued.
2. Provider PENDING stays pending despite deadline age.
3. Transient provider failure stays pending.
4. Scheduler starts and repeats.
5. SQLite migration accepts expired while preserving payment columns/indexes.
6. Admin JSON omits `invoice_url`.
7. Another member cannot retrieve the purchase/invoice URL.
8. Owner sees the resume link for pending + valid URL + future deadline.
9. Paid/failed/expired, invalid-host, and elapsed-deadline records show no resume link.
10. Resume is a normal external link to the existing invoice with `noopener noreferrer`; it does not call checkout.
