# Scoped verification when baseline lint fails

If repository-wide lint fails on pre-existing violations outside the feature diff:

1. Preserve the full lint command and failure count as baseline evidence.
2. Confirm the reported files are unrelated to the feature; do not repair them merely to green the feature gate.
3. Run the linter explicitly against every changed source and test file.
4. Run focused behavioral tests, type-check, and the production build independently rather than chaining them behind the failing full-lint command.
5. Report precisely: repository-wide lint is baseline-blocked; changed-file lint passed or failed. Never summarize this as “lint passed.”

This keeps verification accurately scoped while avoiding unrelated churn.