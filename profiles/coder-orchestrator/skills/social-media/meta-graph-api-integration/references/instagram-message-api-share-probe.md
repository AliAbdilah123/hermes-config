# One-shot Instagram Message API probe for attachment-only shares

Use after a real Instagram webhook delivers an attachment-only event (including a Threads post sent through the Instagram message action) and approved runtime evidence exposes its exact `message.mid`.

## Read-only evidence sequence

1. Identify the service that actually owns the webhook route. Do not assume the similarly named product service owns it; inspect systemd and reverse-proxy routing without printing environment values.
2. Select the newest provider-originated candidate from approved diagnostics. Require an exact raw `message.mid`; a truncated/hash-only diagnostic is not usable as an API identifier.
3. Correlate the narrow journal window and preserve separately:
   - journal receipt time and timezone;
   - provider event timestamp, converted from epoch milliseconds when present;
   - sender, recipient/entry, and MID only when exact-ID access/reporting is authorized;
   - terminal processing result (`processed`, `failed`, `ignored`, reason).
4. Confirm the configured runtime credential by key name/presence only. Never print, interpolate into shell trace, persist, or place it in command output.
5. Make exactly one GET for the observed MID, requesting `fields=message,attachments,shares`. Build and execute it in one process so the token remains internal. Catch HTTP errors and retain their response body.
6. Sanitize structurally before printing. Retain only requested response fields plus `id` and complete useful API error details (`message`, `type`, `code`, `error_subcode`, `fbtrace_id`, `is_transient`, and user-facing error fields). Never print request URLs because query parameters may contain the token.
7. Report the exact HTTP status and distinguish absent fields from empty collections. Explicitly report `shares.data[*].url`, `id`, and `type`; if `shares` is absent, say so rather than inferring an empty share.

## Interpretation boundaries

- `processed=0`, `ignored=1`, `missing_text=1` means domain processing did not run; an attachment may still exist and be inspectable through the Message API.
- HTTP 200 does not guarantee `shares` is present. A response may contain an empty message and attachment object while omitting `shares`; report that provider result exactly.
- An empty template attachment in the webhook and absent `shares` in the Message API are evidence that this MID cannot supply share metadata, not proof that all Threads shares behave that way.
- Do not issue fallback requests with different versions, fields, hosts, or credentials when the user authorized exactly one GET.
- If no exact MID from a fresh suitable event exists, stop. Ask for a new Threads post to be sent through Threads' Instagram message/share action to the configured inbox.

## Minimal report

- event and receipt timestamps;
- exact or clearly labeled hashed IDs;
- whether processing ran and terminal reason;
- one GET's HTTP status;
- sanitized JSON preserving `message`, `attachments`, `shares`, and API error detail;
- explicit `shares.data` URL/ID/type outcome;
- confirmation that no source, database, config, files, or services were changed/restarted.
