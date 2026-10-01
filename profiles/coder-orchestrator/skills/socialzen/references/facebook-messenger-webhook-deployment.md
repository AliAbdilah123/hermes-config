# Facebook Messenger webhook deployment and proof

A passing Meta `GET` verification challenge does not prove inbound Messenger processing. Trace and verify the full path independently:

`POST` route registration → bounded raw body → `X-Hub-Signature-256` over exact bytes → `object=page` parsing → configured Page/recipient checks → stable sender/message IDs → transactional processing and replay deduplication.

## Safe rollout

1. Inspect the running branch and exact systemd `ExecStart`. Facebook identity/store code may exist while the deployed callback still supports only `GET`.
2. Confirm effective configuration by key presence and length only. Never print Page tokens, app secrets, verification tokens, signatures, raw PSIDs, Page IDs, or message bodies.
3. Before touching live SQLite, create a `.backup` and integrity-check it. Start the newly built binary against that copy on an unused port. Require successful migrations, service-specific health, expected Facebook tables/integration row, and another integrity check.
4. Deploy the exact tested binary atomically, restart its service, poll local health, and verify the public nginx callback separately.
5. Run three non-destructive public probes:
   - the real verification challenge echoes correctly;
   - an unsigned POST returns `403`;
   - a correctly signed payload with an intentionally unsupported object returns `200`, logs `processing_ran=false`, and creates neither provider receipts nor notes.
6. These probes establish proxy/signature/backend behavior only. A real Facebook message is still required to prove Meta delivery and obtain real sender/recipient/message evidence.

## Logging contract

Log hashed or truncated sender, recipient/Page, and message identifiers, whether processing ran, and the exact outcome (`note_created`, `activated`, `duplicate`, ignored reason, or error). Keep both per-event logs and a request-level result summary. Ensure the summary carries the relevant hashed IDs rather than always reporting `none`.

Never log raw callback bodies, message content, verification codes, tokens, secrets, or signatures.

## Deployment pitfall

Keep backup, install, restart, health, schema, and public probes as separate commands or explicitly labeled gates. Avoid brittle exact-string checks against `sqlite3` CLI output in a chained deployment: header settings can make a valid `PRAGMA integrity_check` print multiple lines and stop the chain before installation. Inspect and classify each boundary separately before continuing.
