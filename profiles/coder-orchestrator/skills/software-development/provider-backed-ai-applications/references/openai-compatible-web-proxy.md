# OpenAI-compatible web proxy checklist

Use when a browser UI needs real generation through an OpenAI-compatible HTTP API.

## Minimal endpoints

- `GET /api/.../provider/status`: return `configured` and a display-safe model label. Omit the API key and usually omit the internal base URL.
- `POST /api/.../generate`: decode a size-limited JSON body, trim and validate the prompt, select a server-approved model, call the upstream API with a bounded timeout, cap the response body, validate the expected response shape, and return normalized output.

## Failure contract

Use stable application errors for at least:

- provider not configured;
- invalid or oversized prompt;
- upstream unreachable/timeout;
- upstream non-2xx;
- oversized, malformed, or empty upstream response.

The UI must clear loading state and present an actionable error. Never substitute demo output after a failed real request.

## Focused verification

1. Unit test status with configured and unconfigured server state.
2. Use an in-process fake upstream to assert the server adds authorization, sends the selected model/prompt, and normalizes successful content.
3. Test absent credentials, invalid prompt, upstream non-2xx, and malformed/empty response.
4. Run the frontend test for status/menu and failure UI; then run backend tests and the production build.
5. For release readiness, exercise a real configured provider end to end. An unconfigured `503` proves honest failure handling, not successful provider connectivity.
6. For canvas/media products, verify the returned modality matches the selected node. Text chat completion must not be represented as generated image/video media.
