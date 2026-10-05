# Implementation checklist

Provider configuration includes app identity/secret, webhook verification/signature material, graph version, dedicated account/page ID, owner mapping, callback origin, database and secure-cookie settings. Publish callback URLs exactly. Verification codes are random, hashed, short-lived and one-use. Status DTOs expose readiness/account identity but no secrets. Test raw-body signature, retry idempotency, ownership, privacy-safe logs, attachment host redirects, stale lease recovery, cache read authorization, unavailable enrichment omission and later successful retry.
