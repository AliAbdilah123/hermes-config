# Hermes CLI as an application AI provider

Use this pattern when a local/server-hosted application should offer Hermes as an AI provider without exposing credentials to the browser.

## Minimal contract

- Keep provider settings server-side or persist only non-secret values such as `provider = hermes` and an optional model override.
- Invoke Hermes with an argv array via the platform process API (`spawn`/`execFile`), never through a shell.
- Use non-interactive output: `hermes chat -Q -q <prompt>`.
- Mark third-party invocations with `--source tool` so application traffic is distinguishable from user CLI sessions.
- Restrict the launched session to the smallest capability set suitable for text rewriting. Prefer `--safe-mode` when no tools, user rules, plugins, or credentials beyond the configured model are needed.
- Validate model overrides against a conservative identifier grammar before adding `-m <model>` to argv.
- Apply body limits, prompt/context length limits, timeout the child process, terminate it on timeout, and map non-zero exits to a bounded error response.
- Never serialize Hermes credentials, profile config, stderr dumps, or environment values into frontend assets or API responses.

## Selection-context semantics

Keep two client states separate:

1. **Pending message context**: selected text attached to the next outgoing request exactly once, then cleared.
2. **Captured editor range**: note ID plus `from`/`to` positions retained long enough to apply the returned answer.

Clearing the one-shot context must not erase the captured range; otherwise “Replace selection” becomes disabled as soon as the prompt is sent. Invalidate replacement only when the note changes or the stored range no longer matches the intended source text. “Insert below” can remain available as the safe fallback.

## Verification

- A new conversation returns an empty message list; do not seed a synthetic assistant greeting unless requested.
- Provider settings reject any provider other than Hermes and persist the optional model override.
- The exact selected text appears once in the constructed Hermes prompt and is absent from later messages unless reselected.
- The child process is launched with `shell: false`, a finite timeout, and restricted arguments.
- Exercise one real Hermes request through the deployed browser/API path; a mocked response proves only UI wiring.
- After applying an answer, reload the note and verify the edited Markdown persisted.

## Subpath preview pitfall

Do not depend solely on nginx `sub_filter '</head>' ...` to inject an API base. Minimal Vite input HTML may omit a literal closing `</head>`, so the filter silently matches nothing. Put a small runtime base-path bootstrap in `index.html` (or build with an explicit base variable), then verify the public HTML contains it and the API returns JSON under the exact preview prefix.
