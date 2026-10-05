---
name: provider-backed-ai-applications
description: Implement application features that call a local or CLI-backed AI provider through a secure server boundary, including provider settings, context handling, chat persistence, and real end-to-end verification.
---

# Provider-Backed AI Applications

Use this skill when a web or desktop application delegates generation to an installed AI agent/CLI rather than calling a browser-side model API directly.

## Minimal architecture

1. Keep provider invocation server-side. Credentials, provider profiles, OAuth state, and command execution never belong in the browser.
2. Choose the smallest real server boundary already present in the repository. For an OpenAI-compatible HTTP provider, a thin server proxy is enough; do not add a provider framework merely to forward one endpoint.
3. Invoke CLIs with an argument array, not a shell-built command. Bound input size, execution time, output size, and cancellation. For HTTP providers, likewise bound request body, prompt length, response body, and client timeout.
4. Verify the installed CLI or upstream HTTP contract before coding. Use only observed flags and response shapes; provider contracts evolve.
5. Persist non-secret settings separately from credentials. Validate provider and model values at the API boundary. Prefer a server-configured model; if the browser may override it, enforce an explicit server-side allowlist to prevent arbitrary model/billing selection.
6. If only one provider exists, use a direct branch. Do not introduce a provider registry/interface until a second implementation exists.

## OpenAI-compatible browser applications

- Expose a non-secret status endpoint so the UI can honestly distinguish configured, unavailable, and unreachable states. Return only display-safe metadata; never return keys, credential fingerprints, or sensitive internal endpoint details.
- Proxy generation through the application server with the authorization header added there. Never ask the browser to retain a provider key in local/session storage.
- Treat non-2xx upstream status, transport failure, timeout, oversized output, malformed JSON, missing choices, and empty content as explicit failures. Do not replace failure with a canned “generated” result.
- Keep provider capability claims narrow. Chat-completions text output does not implement image/video generation; either connect the matching media endpoint or label the workflow as text generation.
- An unconfigured local run should remain usable for non-AI canvas/editor actions and should show an actionable, honest generation error.

See `references/openai-compatible-web-proxy.md` for a compact endpoint and verification checklist.

## Hermes provider

- Invoke Hermes server-side with the verified non-interactive contract, typically `hermes chat -Q -q <prompt> --source tool` plus an optional validated model override.
- To restrict capabilities while retaining the configured provider and credentials, use `--toolsets safe`. **Do not use `--safe-mode` for application integration**: it implies `--ignore-user-config`, which can remove custom-provider configuration and authentication.
- Omitted model means the active Hermes profile default.
- Treat the Hermes process exit code, stderr, timeout, empty output, and provider-error text as explicit application errors. Some CLI/provider combinations may emit an error-looking stdout payload; do not persist that as an assistant answer solely because output is non-empty.
- Reproduce provider failures with the exact application flags, then compare against a minimal invocation with one flag removed at a time. This distinguishes provider/billing failures from invocation-mode failures.
- Do not expose or copy Hermes credential files into the application.

## Selection-aware chat context

- Capture selected text together with stable document identity and editor range.
- Show pending context visibly and allow removal before send.
- Attach pending context to the next message exactly once, then clear it only after the request is accepted.
- Before applying output, verify the document/range still matches. Disable replacement when stale while retaining a safe insert action.
- Do not seed synthetic assistant messages into empty history unless explicitly requested. Put guidance in placeholders rather than persisted chat.

## Provider settings UX

- Show only implemented providers as selectable.
- A sole provider may be displayed as fixed/disabled while still exposing relevant settings such as model override.
- Persist settings and verify reload behavior.
- Never render secret fields for credentials owned by the server-side provider profile.

For the exact flag-isolation recipe, error interpretation, and false-success guard, see `references/hermes-cli-provider-boundary.md`.

## Verification

Test first and retain focused checks for:

- command argument construction without shell interpolation;
- provider/model validation;
- empty conversation containing no synthetic assistant record;
- selected context consumed exactly once;
- stale-selection replacement refusal;
- timeout, abort, non-zero exit, and empty provider output;
- settings persistence after reload.

Public E2E must invoke the real server-side provider and exercise selection → context drawer → send → response → apply → reload. Mocked provider tests and HTTP 200 probes are supporting evidence only.

## Pitfalls

- A generic “OpenAI-compatible” abstraction is not free when the requested provider is a local CLI.
- Chat help copy accidentally persisted as an assistant message changes history semantics.
- Clearing pending context before request acceptance loses user intent on transport failure.
- Passing prompts through a shell creates injection risk even if UI input appears trusted.
