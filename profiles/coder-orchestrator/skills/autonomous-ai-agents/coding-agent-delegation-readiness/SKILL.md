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
6. Preserve router catalog prefixes exactly (for example, `cx/gpt-*`) in both the readiness probe and full launch. A bare downstream model name can select a different provider or credential pool even when the prefixed catalog entry is healthy.
7. If a preflight or wrong-route launch fails, verify the repository still has the expected branch, unchanged `HEAD`, and no new dirty paths before retrying. Report the corrected route rather than presenting a transient routing failure as an implementation failure.
8. If preflight fails, report the concrete blocker immediately and offer verified alternatives; do not launch the full task first.

Example readiness probe pattern:

```bash
printf '%s\n' 'Respond exactly: READY' | \
  <cli> <run-command> --model <exact-model> <reasoning/speed flags> -
```

## CLI flag compatibility before long launches

After the cheap model probe, inspect the installed CLI's subcommand help (for example, `codex exec --help`) before launching the full job. Automation flags and their placement can change across releases: a documented `--full-auto` may be replaced by `--approve-for-me`, `-a never`, or a bypass flag, and top-level flags may need to precede `exec`. Use only flags rendered by the installed binary.

If a launch fails during argument parsing, verify the repository still has the expected branch, unchanged `HEAD`, and no new dirty paths. Correct the invocation from local help and re-run the cheap probe before announcing active work. For bounded background jobs, enable one-shot completion notification; a process handle alone does not prove the model accepted the goal, so confirm startup output names the expected model/provider and shows the task was received.

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

Provider-specific references:

- Quota probing: `references/9router-quota-checks.md`
- Codex custom-provider routing, stale dashboard-applied model IDs, authentication, compatibility errors, secret-safe fingerprint probes, and verification: `references/9router-codex-provider-setup.md`

## Execution handoff

Before promising the delivery boundary, preflight the repository as well as the coding CLI:

1. Record the current branch, `HEAD`, dirty/untracked paths, and configured remotes.
2. Classify untracked plan/review artifacts created during planning as task-owned; preserve them across branch creation and stage them explicitly rather than treating them as unrelated dirt.
3. Verify remote **write access**, not merely that a remote URL exists, before promising a push. Use a non-mutating permission check where the host supports one; otherwise state that push access is unverified until the actual push. If unavailable, report the boundary early but continue local implementation, verification, commit, and authorized deployment where possible.
4. Create the feature branch from the intended integration base only after baseline ownership is clear.

### Event-driven long-running handoffs

For bounded coding-agent jobs, launch them in the background with the runtime's one-shot completion notification enabled, then end the active turn. Do not repeatedly poll or block waiting for completion; let the completion event re-enter the conversation and trigger review/finalization. Inspect logs or send input only when the user asks, an explicit intervention signal arrives, or the agent is known to require input.

A process handle proves only launch. A completion notification proves exit, not correctness: after it arrives, independently inspect the diff and commit, run fresh scoped tests, and verify push/deploy state.

When a requested model identifier fails, do not normalize or strip catalog/provider prefixes speculatively. Probe the CLI's configured/default model, read the exact identifier it reports, then retry once with that exact identifier and requested reasoning level.

If the user reports that the same CLI works manually, treat that as strong evidence of an invocation/environment mismatch before diagnosing credentials. Compare the automated and manual contexts without exposing secrets: `type -a`/resolved binary, effective top-level model and provider config, HOME/XDG paths, relevant environment-variable **names**, local router listener/catalog, and exact CLI flags. Preserve catalog prefixes such as `cx/`: with a local router they can select the credential pool, while overriding with an unqualified `gpt-*` ID can deterministically route to another provider and produce a misleading “no active credentials” response. Reproduce the working manual route before changing auth or asking the user to reauthenticate.

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

## Delegating strict-TDD work + cheap progress monitoring

When handing a multi-phase, test-first build to an external coding CLI, seed the RED step yourself before launch: write the first failing test, run it, and watch it fail for the right reason. Then pass it with an explicit "a failing test already exists and has been observed failing" anchor in the prompt. This guarantees the subagent cannot silently skip the RED phase, and you own the proof that the anchor actually fails for the intended reason (delegation does not transfer the "watch it fail" obligation).

Make progress observable by contract, not by log-scraping: require one commit per approved phase with an exact, agreed subject line. While the job runs, poll `git log --oneline` + `git status --short` — each phase subject appearing in history is the real progress signal. The process log buffer is the wrong monitor for long jobs: it re-echoes the same stale diff hunks and buries the useful "now doing phase N" lines, so `process log` looks frozen even when work is advancing. (The poll-vs-event guidance above assumes you can end the turn and re-enter on completion; when the runtime returns the result in-turn with no re-entry, poll — but poll the git state signal, never the log buffer.)

After exit, close the loop with a preserve-file audit instead of trusting the "not staged" claim: confirm each protected untracked/dirty path appears in zero commit diffs across the whole range, and that the observed phase subject per commit matches the plan.

```bash
base=<base-sha>   # the commit the work built on
git log --oneline "$base"..HEAD                      # phase subjects = progress
git status --short                                  # dirty/untracked survivors
git log --name-only --format= "$base"..HEAD | grep -E '<preserve-path-pattern>' || echo clean
for c in $(git rev-list --reverse "$base"..HEAD); do git show --format='%s' -s "$c"; done
```

Seeding the anchor also pairs with ponytail: the handoff prompt stays lazy — a few lines of anchor + a terse scope list beats a full spec re-statement.

## Reviewing uncommitted work vs. committed refs

`codex exec review --uncommitted` rejects a positional `[PROMPT]` — it errors with
`the argument '--uncommitted' cannot be used with '[PROMPT]'` even though its own
usage line prints `--uncommitted [PROMPT]`. Do not keep re-trying the same flag with
argv, a heredoc, or stdin: that path will not accept a brief. Options:

- Review a **committed** ref normally: `codex exec review --base origin/main`, or
  feed `git diff base...HEAD` to a plain `codex exec` review prompt.
- For a **large uncommitted** diff, hand it to a Hermes subagent instead:
  `delegate_task(role="leaf", goal="Review the uncommitted diff … concrete findings
  with severity + file/line … do not modify files")`. The subagent's full summary is
  written to a cache file
  (`~/.hermes/profiles/<profile>/cache/delegation/subagent-summary-*.txt`) you can
  `read_file` when the inline summary is truncated. This yields ranked findings
  faster than fighting the `--uncommitted` input path.

## Pitfalls

- Announcing “delegated” immediately after receiving a process ID.
- Checking auth but not quota with the requested model.
- Passing a complex multiline prompt as a fragile quoted argument.
- Calling a provider/model unavailable based only on a transient setup error.
- Listing models that were not actually rendered or successfully probed.
