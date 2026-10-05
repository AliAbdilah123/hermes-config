# Matching, notifications, funnel

Matching returns bounded deterministic total and named contributions; contributions sum to total. Notification insert uses semantic dedupe. Digest selects bounded due rows then closes cursor, sends outside transaction, and persists outcome/backoff. Funnel events are emitted server-side from committed domain actions, use an allowlist and no raw PII metadata; admin API returns bounded aggregates only.
