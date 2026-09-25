# Instagram webhook payload compatibility and runtime repair

Use this after transport and signature verification succeed but real Instagram callbacks return `200` without creating domain records.

## Dual message containers

Do not assume Instagram message events always arrive in one container. Preserve the established `entry[].messaging[]` shape, and support the subscribed-field shape when production logs show `entry.id` populated while decoded sender, recipient, and message IDs are empty:

```json
{
  "object": "instagram",
  "entry": [{
    "id": "<receiver>",
    "changes": [{
      "field": "messages",
      "value": {
        "sender": {"id": "<sender>"},
        "recipient": {"id": "<receiver>"},
        "message": {"mid": "<message-id>", "text": "<text>"}
      }
    }]
  }]
}
```

Normalize recognized events from both containers into one internal event type and feed the existing domain processor. Keep unsupported `changes[].field` values observable and acknowledge them with `200` rather than interpreting them as messages. Add a persistence regression for each supported container; parser-only assertions are insufficient.

## Safe webhook telemetry

Log every POST at receipt and completion, including invalid-signature and malformed-JSON outcomes. Safe fields include object name, entry/change/event counts, sanitized change-field names, processed/ignored/failed counts, explicit ignore-reason counts, and hashed or truncated identifiers.

Never log raw payloads, message text, signatures, access tokens, app secrets, verification tokens, or raw provider IDs. Receipt-only logging is insufficient: pair it with a terminal outcome so accepted-but-ignored deliveries are diagnosable.

## Runtime repair

1. Back up the effective `.env` and live SQLite database. Use `VACUUM INTO` or `.backup`, then require `PRAGMA integrity_check = ok`.
2. Derive the receiver ID from that receiver token's `/me`; update the matching integration ID, not unrelated sender IDs.
3. Resolve fallback ownership from an actual runtime `users` row. Never infer a full email from masked diagnostics. If exactly one user exists and product ownership makes the assignment unambiguous, use that row; otherwise ask which user owns the inbox.
4. Rebuild and replace the exact binary named by systemd `ExecStart`, restart, poll local health through the readiness race, and confirm the integration row has the token-derived receiver ID and non-null owner ID.

## Public verification

1. Send valid HMAC-signed synthetic callbacks through the exact public HTTPS route for both `messaging` and `changes` containers.
2. Assert each persists under the integration owner.
3. Inspect application logs for safe receipt, shape, and outcome metadata.
4. Delete synthetic records and rerun SQLite integrity checking.
5. Require wrong signatures/tokens to remain rejected.

A CDN/WAF may reject a scripted client's default user agent before the request reaches the app. Distinguish edge rejection from signature failure by checking whether application receipt logs exist; retry the same request with a normal explicit user agent rather than weakening webhook security.

Synthetic signed callbacks prove routing, signature validation, parsing, ownership, and persistence. They do not replace the final acceptance gate: one fresh provider-originated DM must arrive and persist.
