# Verifier-required temporary script

Use this when workspace feedback says no canonical command was detected and explicitly requests a temporary verification script, even if direct checks already passed.

1. Create the script with `mktemp /tmp/hermes-verify-XXXXXX.sh` (or an equivalent OS-safe API).
2. Add `set -eu`; run focused changed-behavior tests first, then broad regression, lint/typecheck, and build checks. Cover every changed runtime in mixed-stack work.
3. Run it once against the final workspace state and preserve its exit status.
4. Clean the script and temporary binaries with `trap`/`finally`.
5. Report it as **ad-hoc verification**, not detector-recognized suite green. State focused and broad evidence separately.

A previous direct test/build run does not satisfy feedback that explicitly requires this script shape; rerun through the script.