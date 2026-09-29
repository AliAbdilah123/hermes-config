# Verified Instagram sender-to-profile note routing

Use when a product lets a signed-in user claim an Instagram username, verify ownership by DM, and route later inbound DMs into that user's notes or records.

## Stable identity contract

- Treat the typed username as a claim and display label, not the durable routing key.
- Generate a cryptographically random, short-lived, single-use verification code.
- Persist only a hash of the code with the local user/profile ID, claimed username, expiry, and pending status.
- When the code arrives at the dedicated inbox, bind the webhook `sender.id` (Instagram-scoped sender ID / IGSID) to that pending identity.
- Route every later message by the verified sender ID, not by username. Username changes must not silently reroute ownership.

## Minimal state transition

```text
pending identity + valid unexpired code from sender IGSID
  -> bind IGSID
  -> mark active/verified
  -> consume code
  -> do not create a note from the verification message

active identity + ordinary DM from bound IGSID
  -> create note owned by that identity's local user

unknown IGSID + ordinary DM
  -> acknowledge webhook
  -> create no user-owned note
```

Deduplicate inbound events using the provider message ID. Activation, code consumption, and reply-claim state should be transactional so retries cannot bind twice or send duplicate success replies.

## Critical policy pitfall: unmatched fallback

Do not automatically assign unmatched DMs to the dedicated inbox owner's personal profile. That defeats an allowlist requirement such as “save notes only from my verified Instagram account” and can mix strangers' content into the wrong user's records.

If unmatched retention is required, make it an explicit separate product:

- admin-only quarantine/inbox;
- no user ownership association;
- defined access control, retention, deletion, and privacy policy;
- separate schema/status from normal notes.

Otherwise, accept a valid webhook with `200` and ignore the unmatched event.

## Security and privacy

- Expire codes quickly (for example, 10–15 minutes) and make them single-use.
- Rate-limit code creation and verification attempts.
- Never log raw webhook bodies, message text, verification codes, signatures, tokens, or app secrets.
- Log only sanitized classifications, counts, and hashed/truncated identifiers.
- Validate webhook HMAC before parsing or recording payload details.
- A forwarded valid code binds the account that actually sends it; explain this clearly in the UI and keep the validity window short.

## Existing-code inspection before planning

Trace the repository before proposing new schema or endpoints. Many implementations already contain most of this flow. Check, in order:

1. pending identity schema and unique constraints;
2. code generation, hashing, expiry, and regeneration;
3. webhook signature validation and event parsing;
4. sender-ID activation transaction;
5. active sender-ID note routing;
6. unmatched-event fallback behavior;
7. provider-message deduplication;
8. settings UI and verification-status polling.

Prefer deleting an unsafe unmatched fallback over rebuilding an already-working verification system.

## Verification matrix

Automated checks:

- valid code activates the pending identity and stores sender IGSID;
- verification DM creates no note;
- subsequent DM from verified IGSID creates exactly one correctly owned note;
- replayed provider message ID creates no duplicate;
- DM from another IGSID creates no note for the verified user or inbox owner;
- another local user cannot claim the same stable sender ID;
- logs contain no message text or code.

Live acceptance requires a fresh baseline and unique markers across three layers:

1. public edge received the new Meta POST;
2. application classified and processed it;
3. live database contains the expected owned note—or contains no note for the unmatched-control sender.

An HTTP `200` alone proves only callback acceptance, not correct routing or persistence.
