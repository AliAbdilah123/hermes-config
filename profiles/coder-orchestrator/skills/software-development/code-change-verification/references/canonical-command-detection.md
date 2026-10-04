# When canonical command detection fails

A direct successful test/build invocation can still leave workspace verification classified as unverified when no canonical command was detected.

Before reporting completion:

1. Create an OS-safe temporary script with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".sh", dir="/tmp")` or `mktemp /tmp/hermes-verify-XXXXXX`.
2. Put the project checks and `git diff --check` (or equivalent static diff validation) in the script.
3. Run it against the final workspace state and preserve the exit status.
4. Remove the script when possible and confirm cleanup.
5. Describe the result as **ad-hoc verification**, not “canonical suite green.”

Do this final wrapper run once instead of first running the same commands directly and then repeating them after the verifier rejects the evidence. It complements rather than replaces focused RED evidence in strict TDD.