# Ad-hoc verification when no canonical command is detected

Use this only when the workspace cannot identify a canonical test/lint/build command after code changes.

1. Create a temporary script with the host language's secure tempfile API, under `/tmp`, using a `hermes-verify-` filename prefix. Do not invent a project-local verification artifact.
2. Put only focused checks for the changed behavior in it: the smallest backend test selection, frontend test selection, and relevant compile/type check.
3. Run the script from the owning project directory and preserve its real stdout and exit code.
4. Remove the script after execution when possible. Ensure cleanup also happens on failure (a shell `trap` or an outer command that captures the status, removes the file, then exits with the captured status).
5. Report the result explicitly as **targeted ad-hoc verification**, never as “the full suite is green.” Name each check, its pass/fail count, and the exit code.
6. If the project later exposes a canonical command, run that instead; ad-hoc evidence does not replace canonical suite evidence.

Minimal shell shape generated through an OS-safe tempfile API:

```sh
#!/bin/sh
set -eu
cd /absolute/project/path
<focused backend test>
<focused frontend test>
<typecheck or compile check>
```

Pitfalls:
- A prior successful run becomes stale as soon as relevant files change afterward.
- A broad command that happened to pass is not evidence if the verification tracker requires a recognized canonical command; classify it honestly.
- Do not claim build/lint coverage for commands omitted from the temporary script.
