# Final mutation boundary

Passing evidence is stale after any subsequent source edit, including a small authorization filter, formatting-assisted rewrite, or test cleanup. Run fresh verification after the final mutation and before claiming completion.

When the runtime says no canonical command was detected, do not rely on equivalent commands run earlier. Create one OS-safe temporary script with `mktemp /tmp/hermes-verify-<project>-XXXXXX`, add `set -eu`, and run it against the final tree. Include:

1. focused tests for the changed behavior;
2. the broader affected test suites;
3. static analysis and typechecking for touched languages;
4. production builds for touched deliverables.

Use `trap` to remove the script, clean disposable build artifacts when appropriate, preserve the script's exit status, and report the result explicitly as **ad-hoc verification**, not “suite green.”

For full-stack work, one script should cover both backend and frontend surfaces so the evidence refers to one final workspace state.