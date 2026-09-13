# 9Router as a Codex CLI provider

Use when Codex is configured to send Responses API traffic through a local 9Router instance.

## Minimal diagnosis

1. Confirm the Codex version and inspect `~/.codex/config.toml` without printing secrets.
2. Confirm 9Router is listening and query `GET /v1/models`.
3. Use the **exact router catalog ID** for a routing probe. A bare `gpt-*` name may route as provider `openai`; a catalog entry such as `cx/gpt-*` selects the Codex route. Treat the prefix as routing metadata, not decoration.
4. After applying or re-applying dashboard configuration, compare that catalog ID with the top-level `model = ...` in `~/.codex/config.toml`. Dashboard credential refreshes may leave a stale unqualified model name in place.
5. Run a real one-line `codex exec` request. Health checks and model listings do not prove request compatibility or usable credentials.
6. Compare installed and current 9Router releases when the router accepts the route but rejects the Codex payload. Update before hand-editing payloads or credentials.

## Known-good provider shape

```toml
model_provider = "9router"

[model_providers.9router]
name = "9Router"
base_url = "http://127.0.0.1:20128/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```

Codex custom providers read the key named by `env_key` from the **process environment**. A value stored in `~/.codex/auth.json` alone may not be attached to custom-provider requests.

If 9Router requires its local API key, expose that key to Codex through the named environment variable. Keep any persistent env file mode `0600`, source it from the user's shell profile, and never print the key. Prefer the router's supported dashboard/CLI credential setup over direct database edits; database inspection is diagnostic only.

## Error classification

- `No active credentials for provider: openai`: the bare model name selected the wrong route, or the OpenAI route truly lacks credentials. Retry with the exact `/v1/models` catalog ID before changing credentials. If the prefixed model succeeds through `/v1/responses` using the configured local key, patch only the top-level Codex `model` value and verify with `codex exec`; repeatedly reapplying dashboard credentials will not repair stale routing metadata.
- A redacted config read cannot be reused as an authentication probe: secret-redaction may replace the key with a display placeholder. Perform credential comparisons inside a script, print only fingerprints/status codes, and never send the redacted value.
- `Unknown parameter: input[0].content`: route and credential selection worked, but the installed router is incompatible with the current Codex Responses payload. Check/update 9Router.
- `401 Missing API key`: newer router authentication is active but Codex sent no local router key. Add `env_key`, export that variable, then retry in the same environment.
- Agent-role warnings are independent unless the request itself fails on role parsing.
- Separate deterministic routing/authentication responses from router-process instability. Check the listener and service logs independently: connection resets, incomplete chunked reads, or repeated service restarts are availability failures, while a stable JSON `No active credentials for provider: openai` response is a routing/pool-selection failure. Stabilize the service before interpreting request-level probes.

## Secret-safe direct probes

When several local files may hold the router key, compare them inside one local script and print only a one-way fingerprint, HTTP status, and sanitized response prefix. Never copy a key from `read_file` or tool output into another command: secret redaction may substitute a placeholder, creating a false 401 that says nothing about the real credential. Use the real key only in-process and discard it after probing both the configured and exact catalog model IDs.

## Verification

Run an exact-response probe and require exit code 0 plus model output:

```bash
codex exec --sandbox danger-full-access --skip-git-repo-check \
  -m cx/<exact-model-id> 'Reply with exactly OK'
```

After changing shell startup files, source the profile for the current shell and also note that new shells inherit it automatically.
