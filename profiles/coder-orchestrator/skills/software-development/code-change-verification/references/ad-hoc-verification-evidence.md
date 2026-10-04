# Ad-hoc verification evidence

Use this when the workspace verifier does not recognize a canonical command, even if the repository has a `Makefile` or equivalent.

1. Create the script with `mktemp /tmp/hermes-verify-<project>-XXXXXX`; retain the actual returned path for reporting.
2. Use `set -euo pipefail` and run fresh, uncached behavior tests (`go test -count=1`, or the ecosystem equivalent), static checks, production builds, and a focused runtime smoke test.
3. For server smoke tests, start the server as a tracked background process when tooling requires it. Poll readiness quietly (`curl -fsS ... >/dev/null 2>&1`) until success, then execute explicit live/ready assertions. A loop that merely expires is insufficient: record readiness in a flag or make a final mandatory request.
4. Preserve the script exit code and remove the script plus temporary binaries, databases, and logs with a trap.
5. Report this specifically as **ad-hoc verification**, not “suite green.” Quote only evidence from the latest run.
6. Report the exact temporary path actually used. Never reuse a path or runtime claim from an earlier run, and do not claim startup/health/database evidence if the latest script only ran tests and builds.

A successful final marker is useful only after every preceding command and runtime assertion is guarded by `set -e` and has genuinely passed.
