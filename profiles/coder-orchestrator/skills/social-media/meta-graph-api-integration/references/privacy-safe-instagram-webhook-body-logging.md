# Privacy-safe Instagram webhook body logging

Use when operators need enough payload visibility to debug Meta webhook shape/routing without persisting DM contents or secrets.

## Contract

- Keep the existing bounded body read (`http.MaxBytesReader` or equivalent).
- Validate `X-Hub-Signature-256` against the exact raw bytes before emitting any body-derived log.
- Parse JSON before logging. Invalid signatures, unsigned requests, oversized bodies, and malformed JSON must not emit a body log.
- Recursively walk objects and arrays and replace every key named `text` with a fixed marker such as `[redacted]`; do not assume text exists only at `entry[].messaging[].message.text` because Meta payload variants can nest events under `changes[].value`.
- Re-marshal the sanitized value into one compact structured line with a stable marker such as `instagram webhook body=` for `journalctl` filtering.
- Never log request headers, signatures, app secrets, access tokens, verify tokens, or the original raw payload. Keep existing hashed-ID logging unless temporary raw-ID diagnostics were explicitly approved and time-bounded.
- Preserve callback response and event-processing behavior; observability must not change routing or persistence.

## TDD matrix

Write and observe failing tests first, then implement minimally:

1. Valid signed messaging payload logs compact JSON and replaces message text.
2. Valid signed `changes[].value` payload also replaces nested text.
3. Echo/ignored events still produce the sanitized body log after authentication.
4. Invalid or missing signature returns `403` and emits no body log.
5. Correctly signed malformed JSON returns `400` and emits no body log.
6. Sentinel message text, app secret, and signature material are absent from captured logs.

Avoid assertions that depend on JSON object key order after decode/re-marshal. Assert the stable log marker and required fragments independently.

## Deployment verification

1. Run the focused logging regression, then the complete backend suite and build.
2. Replace the exact binary named by systemd, restart, and poll local health.
3. Send a signed diagnostic payload containing a unique private sentinel and an ignored/echo event so verification has no domain side effect.
4. Require `200`, find exactly the sanitized body marker in `journalctl`, and assert the sentinel is absent.
5. Send the same payload unsigned through the public callback; require `403`, a `signature_invalid` result, and no additional body log.
6. If one broad verification command times out, do not treat it as evidence. Split health, signed callback, unsigned callback, and journal assertions into bounded probes to isolate the slow boundary.

A synthetic signed request proves callback security and redaction behavior, not that Meta delivered a real user DM. Real-delivery acceptance still requires a fresh Meta POST correlated to a user-sent marker and persisted outcome.