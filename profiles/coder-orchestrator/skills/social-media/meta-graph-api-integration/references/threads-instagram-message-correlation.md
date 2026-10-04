# Correlating Threads shares delivered as multiple Instagram messages

Use when one Threads share action appears to produce adjacent Instagram webhook events, such as an empty `template` attachment followed by a plain-text message.

## Required Message-node probe

For each distinct `message.mid`, query explicitly:

```text
fields=message,attachments,shares{data{name,description,type,url,id}}
```

Meta requires `shares` subfields to be requested. Keep every response tied to its own MID. A successful HTTP response with no `shares` means that Message node exposed no share data; do not merge fields from a neighboring event.

The diagnostic must be non-blocking: lookup failures must not prevent webhook verification, sender routing, or note persistence. Skip the request when the token or MID is empty. Log only a hashed MID and structural shape/result; never log tokens or request URLs.

## Multi-event correlation boundary

A provider action may arrive as nearby events from the same sender, for example:

1. MID A: `attachments=[{type:"template", payload.generic.elements:[]}]`
2. MID B: `text="..."`

A Message lookup for MID A may expose `attachments.data[].generic_template` with fields such as a subtitle and temporary Instagram CDN `media_url`, while MID B may return only its text and ID.

Same sender, recipient, and close timestamps are **not proof** that both MIDs represent the same source post. Never attach MID A's preview, subtitle, URL, or inferred identifier to MID B's note unless Meta supplies a shared stable identifier or the user explicitly confirms the match. Report each MID separately.

## CDN and cache-key pitfalls

A generic-template `media_url` is a temporary preview asset, not a canonical post permalink. Query parameters such as `ig_cache_key` may decode to a numeric value, but that value is only a heuristic candidate. Do not label it an Instagram or Threads media ID unless an authoritative API lookup returns the corresponding media object/permalink.

A transient Graph error while probing a candidate does not confirm or disprove ownership. Report it as unconfirmed and avoid persistence.

## Safe product behavior

- Process a text MID normally when sender verification succeeds.
- Keep unmatched template events unresolved or ignored according to product policy.
- Preserve MID-based deduplication independently for each event.
- Prefer a user-supplied canonical Threads URL or explicit user confirmation over temporal correlation.
- If presenting candidates, label them as candidates; never silently associate them.

## Verification

Tests should prove:

1. Exact URL encoding of the expanded `fields` expression.
2. Empty token/MID causes no request.
3. Diagnostic transport/API failure does not block normal webhook processing.
4. Logs omit token values, request URLs, raw provider errors, and private message content.
5. Adjacent MIDs remain independent unless an explicit provider linkage exists.
