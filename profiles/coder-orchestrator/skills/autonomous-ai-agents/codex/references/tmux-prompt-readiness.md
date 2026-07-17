# Avoiding tmux prompt-readiness races

## Symptom

A tmux-backed runner launches interactive Codex and immediately injects a task with `tmux send-keys`. The task text appears before or during the Codex startup banner/MCP boot, while Codex later remains at its empty prompt. Captured timelines may repeat the startup banner and injected text.

## Root cause

Process creation only proves the Codex process started; it does not prove its interactive input UI is ready. Sending keystrokes immediately after `tmux new-session` races initialization, authentication notices, MCP startup, and terminal redraws.

## Preferred fix for autonomous jobs

Launch one-shot Codex with the prompt as an argv element:

```text
codex [configured flags...] exec "<full task prompt>"
```

When constructing commands without a shell, append two argv entries—`exec` and the complete prompt. Do not shell-quote the prompt yourself; `exec.Command`/equivalent passes it literally.

Keep tmux only as the durable process/output container. Do not send the initial Codex prompt with `send-keys`.

## Mixed CLI runners

Apply this behavior by CLI type. Codex autonomous jobs use `exec`; another CLI that genuinely requires an interactive session may retain `send-keys`. Preserve configured Codex flags and order by appending `exec`, then the prompt.

## Regression test

Test command construction separately from tmux:

- configured argv remains unchanged,
- Codex result ends with `exec`, `<full prompt>`,
- initial `send-keys` is disabled for Codex,
- non-Codex interactive tools retain their existing behavior.

Then run the full test suite and a real service/job smoke if deployment is requested.
