# Ad-hoc verification script pitfalls

Use this when workspace verification metadata does not recognize a canonical command, even if the repository has obvious package scripts.

## Required shape

1. Create the script with an OS-safe path such as `mktemp /tmp/hermes-verify-<project>-XXXXXX.sh`.
2. Enable `set -euo pipefail` so a failed intermediate check makes the aggregate verification fail.
3. Run focused behavior tests, build/type checks, structural assertions, and `git diff --check` from the intended project directory.
4. Capture the script's exit status, remove the temporary script, and return that status.
5. Report the result explicitly as **ad-hoc verification**, not as canonical suite verification.

## Structural assertions

Prefer a small Python block over deeply escaped shell regexes. Test the assertion independently if it contains nested quoting or backslashes: a malformed verifier can falsely fail valid code.

```bash
verify=$(mktemp /tmp/hermes-verify-project-XXXXXX.sh)
chmod 700 "$verify"
# Write checks to "$verify" using the file-writing facility or carefully quoted printf.
"$verify"
status=$?
rm -f "$verify"
exit "$status"
```

## Evidence discipline

- A failed first verifier does not invalidate later evidence when the failure is in the verifier itself; fix the verifier and rerun the entire script from the final workspace state.
- Distinguish passing checks from warnings. Report persistent warnings separately and never call output pristine when warnings remain.
- Do not infer selector consolidation from raw occurrence counts when responsive/state rules intentionally remain. Assert that superseded visual override fragments are absent and canonical base declarations are present.
