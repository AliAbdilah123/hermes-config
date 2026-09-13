# Hermes CLI provider-boundary diagnosis

Use when an application invokes `hermes chat` server-side and receives authentication text or a false assistant response.

## Reproduction ladder

Run the exact application argv first, then remove or substitute one flag at a time:

```bash
hermes chat -Q --source tool --safe-mode -q 'Reply exactly OK'
hermes chat -Q --source tool -q 'Reply exactly OK'
hermes chat -Q --source tool --toolsets safe -q 'Reply exactly OK'
```

Interpretation:

- If normal and `--toolsets safe` succeed but `--safe-mode` fails authentication, the key is probably valid. `--safe-mode` implies `--ignore-user-config`, so a custom provider's URL/key/model can disappear.
- If every form fails, inspect provider configuration, credential status, and billing independently.
- Use the exact application process environment and profile. Confirm config paths with `hermes config path` and `hermes config env-path`.

## Correct restricted invocation

For an application that needs configured inference but minimal tools, prefer:

```text
hermes chat -Q --source tool --toolsets safe -q <prompt>
```

Invoke with an argv array and `shell: false`. Add a validated `-m <model>` only when the user configured an override.

## False-success guard

Do not equate non-empty stdout with a successful model answer. Require process exit code 0, non-empty output, and reject recognized provider-error payloads if the installed CLI can print them to stdout. Persist the assistant message only after this validation. Keep the user's submitted message when generation fails so history reflects the attempted request.

## Verification

Retain a command-construction test asserting:

- `--safe-mode` is absent;
- `--toolsets safe` is present;
- no shell is used;
- abort/timeout terminates the child;
- chunks are streamed while the complete final response is retained.

Then run a real boundary probe and the public flow: select text → attach exact context once → send → stream → apply → reload and confirm persistence.
