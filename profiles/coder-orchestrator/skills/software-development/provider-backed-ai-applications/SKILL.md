---
name: provider-backed-ai-applications
description: Implement application features that call a local or CLI-backed AI provider through a secure server boundary, including provider settings, context handling, chat persistence, and real end-to-end verification.
---

# Provider-Backed AI Applications

Use this skill when a web or desktop application delegates generation to an installed AI agent/CLI rather than calling a browser-side model API directly.

## Minimal architecture

1. Keep the provider invocation server-side. Credentials, provider profiles, OAuth state, and command execution never belong in the browser.
2. Invoke CLIs with an argument array, not a shell-built command. Bound input size, execution time, output size, and cancellation.
3. Verify the installed CLI contract with its current `--help` before coding. Use only observed flags; provider CLIs evolve.
4. Persist non-secret settings separately from credentials. Validate provider and model values at the API boundary.
5. If only one provider exists, use a direct branch. Do not introduce a provider registry/interface until a second implementation exists.

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
