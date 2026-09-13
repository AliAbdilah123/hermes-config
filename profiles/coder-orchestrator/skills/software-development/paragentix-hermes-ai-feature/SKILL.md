---
name: paragentix-hermes-ai-feature
description: "Use when implementing or reviewing an AI feature that calls the Hermes provider in Paragentix. Reuse the project's authenticated OpenAI-compatible session API, workspace-scoped configuration, durable job lifecycle, progress synchronization, restart reconciliation, and existing Go test patterns instead of inventing another provider path."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [paragentix, hermes, ai, provider, go, sessions]
    related_skills: [hermes-agent, test-driven-development, code-change-verification]
---

# Paragentix Hermes AI Feature

## Overview

Paragentix already integrates Hermes as its AI runtime. Extend that path; do not add a second LLM SDK or call an upstream model provider directly.

Source baseline inspected at commit `f542005f4b8cf4023cce9c8dde2d596da8cca176`:

- `internal/board/scheduler.go` — Hermes HTTP client, session continuation, progress sync, completion, and restart reconciliation.
- `internal/board/settings.go` — workspace-scoped Hermes URL/key/model validation and secret-safe responses.
- `internal/board/migrations.go` — persisted workspace Hermes configuration.
- `internal/board/events.go` — job replies and approval flow.
- `internal/board/app_test.go` and `internal/board/job_review_workflow_test.go` — mock-server contract and lifecycle tests.

Re-inspect these files before implementation because this skill describes a moving codebase, not a frozen API.

## When to Use

Use for a Paragentix feature that:

- asks Hermes to generate, classify, summarize, analyze, plan, or implement;
- needs a multi-turn AI conversation;
- displays Hermes progress or final replies;
- must survive a Paragentix process restart;
- adds an AI-backed job or workflow state transition.

Do not use for deterministic transformations that Go or SQL can perform directly. Do not add an abstraction for a single call site unless two real implementations already exist.

## Existing Contract

### Configuration

Hermes settings are workspace-scoped columns:

- `workspaces.hermes_url`
- `workspaces.hermes_api_key`
- `workspaces.hermes_model`

The settings API accepts only `http` or `https`, requires a key on first save, retains the existing key when an update submits an empty key, and never returns the key. It returns only `hermes_api_key_set`.

Preserve these boundaries. Never log, return, place in events, or interpolate the API key into an error intended for users.

### Completion request

The canonical call is `runHermesSession` in `internal/board/scheduler.go`:

```http
POST {normalized_hermes_url}/v1/chat/completions
Authorization: Bearer <workspace key>
Content-Type: application/json
X-Hermes-Session-Id: <stable session id>   # omit only for a genuinely new stateless call

{"model":"<workspace model>","messages":[{"role":"user","content":"<prompt>"}]}
```

Base URL normalization deliberately accepts both a server root and a URL ending in `/v1/`:

```go
strings.TrimSuffix(strings.TrimRight(base, "/"), "/v1") + "/v1/chat/completions"
```

The expected final response is OpenAI-compatible:

```json
{"choices":[{"message":{"content":"..."}}]}
```

Use a request context, close the response body, cap reads (`4 << 20` currently), reject HTTP status `>= 300`, reject malformed JSON or empty choices, and propagate an actionable error.

### Session identity

For a durable conversation, generate one opaque session ID when the workflow starts, store it with the run as `hermes-api:<session-id>`, and send the raw ID through `X-Hermes-Session-Id` on every continuation.

Do not create a new session for feedback, approval, retry, or implementation continuation. Resume the latest stored Hermes session and existing run unless the product behavior explicitly starts a separate conversation.

### Session inspection

Paragentix reads Hermes metadata through authenticated endpoints:

```http
GET /api/sessions/{session-id}
GET /api/sessions/{session-id}/messages
Authorization: Bearer <workspace key>
```

Session metadata supplies `ended_at`, `end_reason`, and optional `title`. Messages supply `id`, `role`, `content`, `reasoning`, and `tool_calls`.

Only expose assistant-authored text. Never expose user messages, tool results, or raw tool arguments. For assistant tool-call turns with empty content, the current UI-safe fallback is trimmed `reasoning` text.

Use the provider message ID as the deduplication key. If absent, derive a deterministic content key; Paragentix currently hashes role, index, and normalized content. Persist with a database uniqueness constraint plus `INSERT OR IGNORE`, not an in-memory-only set.

## Implementation Workflow

### 1. Prove AI is necessary

Write one sentence describing why deterministic Go/SQL cannot satisfy the feature. If it can, stop and implement the deterministic path. Completion: the feature has a genuinely model-dependent output.

### 2. Trace the nearest existing workflow

Inspect the current versions of the files listed in Overview. Identify:

- trigger/API handler;
- owning workspace and authorization rule;
- prompt construction;
- new versus resumed session behavior;
- persisted state/event destination;
- success, blocked, retry, and restart transitions.

Completion: every new transition maps to an existing state and durable row, or a schema change is explicitly justified.

### 3. Add the smallest vertical slice

Prefer calling `runHermes` for a one-shot response or `runHermesSession` when conversation identity matters. Extend `runHermesJob` only when the feature belongs to the durable job scheduler.

Keep prompt construction near the workflow. Include only trusted project context and required user input. Treat model output as untrusted data before using it in SQL, HTML, shell commands, file paths, or state transitions.

Completion: one request travels from an authenticated Paragentix action through Hermes and persists or returns the intended result.

### 4. Preserve lifecycle atomicity

For job-backed work, update job state, run state, and user-visible events in one transaction before launching asynchronous work. Commit before starting the goroutine. On completion, transactionally persist the final reply, mark the run done, move review-phase work to `in_review` or implementation-phase work to `done`, and append the status event.

On provider/network/parse failure, call the existing blocking path so both run and job record the failure. Never mark a run done before its durable final output is written.

Completion: process interruption cannot leave a visible state transition without its matching run/event record.

### 5. Support continuation only when needed

If feedback or approval continues the same task, reuse the session header. Keep the review gate: proposal first, explicit approval, then implementation. Do not collapse review and implementation into one prompt unless the requested product behavior explicitly removes that gate.

Completion: a mock server observes the same session ID on initial and follow-up requests.

### 6. Reconcile durable work after restart

If the new feature creates a long-running Hermes job, make restart behavior query Hermes session metadata/messages rather than declaring it missing. The current rules are:

- final assistant output exists: persist intermediaries, sync title, finish run;
- session ended without output: block with its end reason or a safe fallback;
- session still active: restore running state and poll;
- Hermes inspection temporarily fails: keep watching only if the local run is still active.

Completion: a test reconstructs an active persisted run and reaches the correct terminal or resumed state without issuing a duplicate completion request.

### 7. Verify with the existing test style

Use `httptest.NewServer`; never call a live model in unit tests. Assert at least:

- exact path `/v1/chat/completions` for root and `/v1/` base forms as relevant;
- bearer authorization is present without printing its value;
- model and prompt request fields;
- stable `X-Hermes-Session-Id` for continuations;
- non-2xx and malformed/empty responses fail safely;
- secrets are absent from settings responses and events;
- progress excludes tool/user payloads and deduplicates repeated polling;
- expected database lifecycle transition.

Run:

```bash
go test ./internal/board
```

Then run any frontend tests/build if UI changed. Completion: fresh commands exit zero and the diff contains no secret or unrelated generated artifact.

## Minimal One-Shot Pattern

Use the existing client rather than creating a provider package:

```go
output, err := a.runHermes(ctx, workspaceID, prompt)
if err != nil {
    fail(w, http.StatusBadGateway, err.Error())
    return
}
jsonOut(w, http.StatusOK, map[string]string{"output": output})
```

Before copying this pattern, enforce endpoint authentication/authorization, bound user input, and decide whether the result must be durable. If it must survive refresh/restart or accept follow-ups, use the job/session lifecycle instead.

## Common Pitfalls

1. **Calling OpenAI, Anthropic, or another model vendor directly.** Hermes is the provider boundary; direct calls bypass workspace model selection and session/tool behavior.
2. **Appending `/v1` blindly.** A configured `/v1/` base then becomes `/v1/v1/...`; use the established normalization.
3. **Losing session identity.** A follow-up without `X-Hermes-Session-Id` starts disconnected context.
4. **Leaking tool payloads.** Session messages can contain commands, arguments, and results; expose only normalized assistant text.
5. **Leaking credentials.** Never serialize the saved key back to the frontend or include request headers in errors.
6. **Duplicate progress events.** Polling repeats messages; rely on stable source keys and a database uniqueness constraint.
7. **Goroutine before commit.** The worker can race ahead of durable run state; commit first.
8. **Treating restart as failure.** Inspect Hermes session state and reconcile before blocking.
9. **Trusting model output.** Validate it at every execution or persistence boundary.
10. **Testing only the happy-path body.** Assert headers, URL normalization, failures, lifecycle state, and secret absence.

## Verification Checklist

- [ ] Re-inspected current Paragentix Hermes integration files.
- [ ] Reused workspace-scoped URL, key, and model.
- [ ] Reused `/v1/chat/completions` and bearer authentication.
- [ ] Reused a stable Hermes session ID when the workflow is conversational.
- [ ] Did not expose API keys, user messages, tool output, or raw tool calls.
- [ ] Persisted lifecycle changes atomically before asynchronous execution.
- [ ] Added restart reconciliation for new durable work.
- [ ] Added focused `httptest` coverage.
- [ ] `go test ./internal/board` passes freshly.
- [ ] UI changes, if any, were inspected and verified separately.
