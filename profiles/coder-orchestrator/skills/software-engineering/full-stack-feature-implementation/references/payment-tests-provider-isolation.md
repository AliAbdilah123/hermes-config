# Payment integration tests: isolate provider configuration

Use for checkout tests when the application can call a real or test-mode payment provider based on inherited environment/configuration.

## Durable rule

A checkout test must own its provider boundary. Do not infer the expected HTTP status from whether credentials happen to exist in the shell.

## Pattern

1. Start a local fake HTTP server implementing the provider invoice endpoint.
2. Save and restore every provider-related config field or environment variable with the test framework cleanup mechanism.
3. Point the app at the fake server and set an explicit fake credential/token.
4. Perform checkout.
5. Assert one deterministic success response and inspect the captured provider request for purchase ID, amount, and redirect metadata.
6. Add a separate fake-provider failure test when controlled 502 behavior matters.

If the application's config is loaded before the test can change environment variables, override the constructed app config directly or construct the app only after setting test-owned values.

## Anti-pattern

```go
if status != http.StatusOK && status != http.StatusBadGateway { ... }
```

Accepting both success and provider failure makes the test environment-dependent and can silently create external test invoices. It also stops proving whether checkout integration actually works.

## Verification

- No network request leaves the local fake server boundary.
- The success test always returns the same status regardless of developer/CI environment.
- The failure test returns a controlled JSON error.
- Test logs and fixtures contain no real secrets.
