# OpenAI-Compatible Base URL Normalization

## Trigger

An OpenAI-compatible provider returns `404 Not Found` even though its configured API URL and credentials are valid.

## Diagnosis

Inspect the exact URL assembled by the client. A common failure is unconditional version-path concatenation:

- Saved base: `http://host:port/v1/`
- Client suffix: `/v1/chat/completions`
- Broken request: `http://host:port/v1/v1/chat/completions`

Read the provider configuration from the application's real persistence layer (for example SQLite), masking secrets. Probe both candidate URLs with the saved model/key:

1. `trim(base) + /v1/chat/completions`
2. `base-with-one-v1 + /chat/completions`

A 404 on the doubled path and 200 on the single-version path isolates URL construction as the root cause.

## Minimal fix

Normalize the base at the shared request-construction boundary so configurations both with and without a trailing `/v1` work. Do not patch individual callers or rewrite stored user configuration.

Be conservative: remove only a terminal `/v1` path segment after trimming trailing slashes, then append `/v1/chat/completions`. Do not globally replace `v1`, because it may legitimately occur in hostnames or earlier path segments.

## Regression check

Use an `httptest` server that:

- accepts only `/v1/chat/completions`;
- returns 404 for every other path;
- stores a provider base ending in `/v1/` through the same DB-backed configuration path used in production;
- calls the real provider method and asserts the parsed response.

Run the targeted test first (confirm RED before fixing), then the full suite. Finally, probe the real DB-backed configuration without printing the API key.