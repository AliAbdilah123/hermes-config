# SQLite text date filters must match stored date format

Use when a frontend/API date filter returns zero or missing rows even though SQLite contains the expected month/day records.

## Symptom

- DB rows store dates as `YYYY-MM-DD` text, e.g. `2026-07-04`.
- Frontend sends filter bounds produced by JS/date-library `.toString()`, e.g. `Wed, 01 Jul 2026 00:00:00 GMT` or `Sat, 01 Jul 2026 ...`.
- API applies string predicates such as `date >= ? AND date <= ?`.
- Result: lexicographic comparison excludes valid rows, so a month appears empty.

## Triage

1. Inspect the DB schema and sample values:
   ```bash
   sqlite3 sqlite.db ".schema transactions"
   sqlite3 sqlite.db "select date,id,summary from transactions where date like '2026-07%' order by date desc limit 5;"
   ```
2. Probe the exact deployed API query with both formats:
   ```bash
   curl -sS -b 'session=...' 'http://127.0.0.1:PORT/api/transactions?gte.date=Wed,%2001%20Jul%202026%2000:00:00%20GMT&lte.date=Fri,%2031%20Jul%202026%2023:59:59%20GMT'
   curl -sS -b 'session=...' 'http://127.0.0.1:PORT/api/transactions?gte.date=2026-07-01&lte.date=2026-07-31'
   ```
3. Trace frontend date state/helpers for `.toString()`, `.toUTCString()`, `Date.toString()`, or locale output used as API params.

## Fix pattern

At the API boundary, send dates in the same comparable format stored in SQLite:

```ts
transactionFilterStart: dayjs().utc().startOf('month').format('YYYY-MM-DD'),
transactionFilterEnd: dayjs().utc().endOf('month').format('YYYY-MM-DD'),
```

For previous/next month navigation, keep the same format when updating state:

```ts
transactionFilterStart: nextStart.format('YYYY-MM-DD'),
transactionFilterEnd: nextEnd.format('YYYY-MM-DD'),
```

## Verification

- Build/typecheck the frontend.
- Fetch the public/deployed asset or API and confirm corrected query params return expected rows.
- If the user provided a logged-in user id, count that user's accessible wallets/transactions directly in SQLite and compare to API response for the same filter.
