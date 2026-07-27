---
name: coding-agent-delegation-readiness
description: Preflight and safely launch named external coding CLIs/models before promising delegated implementation.
version: 1.0.0
metadata:
  hermes:
    tags: [coding-agents, delegation, cli, preflight, orchestration]
---

# Coding Agent Delegation Readiness

Use when a user requires implementation through a named external coding CLI/model (Codex, Claude Code, OpenCode, or similar), especially with a requested reasoning level or speed tier.

## Preflight before announcing delegation

1. Resolve the exact CLI binary and version.
2. Check authentication without exposing tokens.
3. Run a cheap one-line probe using the **exact requested model, reasoning variant, and service/speed tier**.
4. Treat login and model-cache presence as insufficient: an authenticated account may have exhausted quota.
5. Only tell the user the agent is working after startup output confirms the model accepted the task. A background process handle proves only that a process launched.
6. If preflight fails, report the concrete blocker immediately and offer verified alternatives; do not launch the full task first.

Example readiness probe pattern:

```bash
printf '%s\n' 'Respond exactly: READY' | \
  <cli> <run-command> --model <exact-model> <reasoning/speed flags> -
```

## Reliable multiline prompts

Long prompts with quotes, backticks, or shell-sensitive text should go through stdin rather than one giant argv string:

```bash
python3 - <<'PY' | <cli> <run-command> <flags> -
print('''<multiline task prompt>''')
PY
```

This avoids prompt-loss failures such as “No prompt provided.”

## Capability and quota inventory

When asked what agents/models are available, distinguish four states:

- installed,
- authenticated,
- model identifier accepted,
- quota/request currently usable.

For a direct quota question, inspect the quota authority the user names first (for example a local routing dashboard), rather than opening the downstream coding CLI and treating session context as account quota. Discover the local service and its quota endpoint/UI; if authentication is required, reuse an existing authenticated session when available or ask only for the credential needed to continue. A process launch, active model label, and “100% context left” are not evidence of remaining rolling or weekly allowance.

Report only models and quota values actually confirmed by the authoritative CLI, API, or dashboard. Do not infer a full catalog or allowance from one active model or config file.

Provider-specific 9Router quota probing notes are in `references/9router-quota-checks.md`.

## Execution handoff

For implementation prompts include:

- repository/workdir and project instructions,
- approved plan/prototype paths,
- exact scope and non-goals,
- test-first requirement and verification commands,
- browser/viewport acceptance checks when UI is involved,
- deployment authorization and destination,
- task-only commit/push constraints,
- explicit protection for unrelated untracked files.

After completion, independently verify claimed side effects: inspect diffs, run tests/build, check deployment HTTP, and confirm commit/push state before reporting success.

## Pitfalls

- Announcing “delegated” immediately after receiving a process ID.
- Checking auth but not quota with the requested model.
- Passing a complex multiline prompt as a fragile quoted argument.
- Calling a provider/model unavailable based only on a transient setup error.
- Listing models that were not actually rendered or successfully probed.
