# Canonical plus focused verification

Use both layers before calling code changes verified:

1. Run deterministic focused tests for the touched behavior.
2. Run the repository/workspace canonical command requested or detected by verification metadata, even if it crosses layers (for example, a frontend build after backend work).
3. Report focused and canonical results separately; focused passing tests alone are not full workspace verification.
4. If a broad, non-canonical suite hangs on unrelated live-network behavior, report that concrete blocker. Still run the canonical command and focused tests; the hanging suite substitutes for neither.

A warning with exit code 0 is a passing command with a noted warning, not a failure.