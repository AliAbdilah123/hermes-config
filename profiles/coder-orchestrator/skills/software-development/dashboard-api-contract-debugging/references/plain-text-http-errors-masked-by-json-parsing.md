# Plain-Text HTTP Errors Masked by JSON Parsing

## Symptom

A CRUD form shows `Unexpected token '<letter>'` instead of a useful server error. The letter may be the first character of a plain-text response such as `constraint failed` or `column ...`.

## Root cause

A shared fetch wrapper parses every non-empty body as JSON before checking `response.ok`. Go `http.Error`, a proxy, or a legacy endpoint can return text, so `JSON.parse` throws first and masks the actual failure.

## Diagnosis

1. Trace the message to the shared request wrapper, not merely the form toast.
2. Capture status, content type, body, and the browser's exact request payload.
3. Replay with equivalent authentication and a disposable marker; clean up successful writes.
4. Treat error masking and the underlying server rejection as separate bugs.
5. A handcrafted request succeeding does not disprove a browser-specific payload/state failure.

## Minimal fix

Preserve text for failed responses while rejecting malformed successful responses:

```ts
const text = await response.text();
let json: any = {};
try {
  json = text ? JSON.parse(text) : {};
} catch {
  if (!response.ok) throw new Error(text || response.statusText);
  throw new Error('Invalid API response');
}
if (!response.ok) throw new Error(json?.message || text || response.statusText);
return json;
```

Prefer content-type-aware parsing when the client contract supports it. Do not silently return text on successful endpoints whose callers require structured JSON.

## Verification

- Assert a non-2xx plain-text response surfaces its body, not a `SyntaxError`.
- Assert malformed 2xx JSON fails as a protocol error.
- Run typecheck/build.
- For a deployed form, use authenticated public browser E2E: submit a uniquely marked record, require no page/console error, verify persistence, then remove it.
- Confirm public HTML references the new bundle; HTTP 200 alone is not deployment proof.

## Pitfalls

- Toast formatting cannot recover an error already replaced by `JSON.parse`.
- Direct API success is supporting evidence, not proof that the form's actual payload works.
