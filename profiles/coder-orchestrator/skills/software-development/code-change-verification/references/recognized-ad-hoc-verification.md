# Recognized ad-hoc verification after code changes

Use this when project checks pass directly but workspace verification still reports `unverified` because no canonical command was detected.

1. Treat `unverified` as an unmet delivery gate; do not report completion based only on the prior direct run.
2. Create an unpredictable script path with `mktemp /tmp/hermes-verify-XXXXXX` (or an OS-equivalent secure tempfile API).
3. Put focused changed-behavior tests first, then broader tests, static checks, and production builds needed for every changed path.
4. Run the script against the final workspace state and preserve its exit status.
5. Remove the script and temporary build artifacts when possible.
6. Confirm the execution result records passing `ad_hoc` verification evidence.
7. Report this explicitly as **ad-hoc verification**, list the commands/scope actually covered, and do not call it canonical suite green.

A Makefile or plausible `make check` target does not override the verifier's status: recognized evidence is the acceptance condition.