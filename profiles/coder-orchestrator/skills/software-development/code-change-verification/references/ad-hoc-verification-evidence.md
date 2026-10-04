# Ad-hoc verification evidence

Use this when the workspace verifier does not recognize a canonical command, even if the repository has a `Makefile` or equivalent. Treat verifier metadata as a separate acceptance gate from directly running project commands: after the last edit, run this script even when the same tests/build just passed individually, so final evidence is both fresh and recognizable.

1. Create the script with `mktemp /tmp/hermes-verify-<project>-XXXXXX`; retain the actual returned path for reporting.
2. Use `set -euo pipefail` and run fresh, uncached behavior tests (`go test -count=1`, or the ecosystem equivalent), static checks, production builds, and a focused runtime smoke test.
3. For server smoke tests, start the server as a tracked background process when tooling requires it. Poll readiness quietly (`curl -fsS ... >/dev/null 2>&1`) until success, then execute explicit live/ready assertions. A loop that merely expires is insufficient: record readiness in a flag or make a final mandatory request.
4. Preserve the script exit code and remove the script plus temporary binaries, databases, and logs with a trap.
5. Report this specifically as **ad-hoc verification**, not “suite green.” Quote only evidence from the latest run.
6. Report the exact temporary path actually used. Never reuse a path or runtime claim from an earlier run, and do not claim startup/health/database evidence if the latest script only ran tests and builds.
7. When verifier metadata explicitly says `unverified`, treat that as the controlling gate even if a repository-native command (such as `make check`) just passed. Run one final temporary verifier after the last edit, make it directly reference every reported changed path, and describe only that run as the completion evidence. Repository-native results may be mentioned separately as supplemental evidence, never as a substitute for the requested ad-hoc gate. Do not answer the status message by arguing that earlier commands passed; perform the requested verification shape.
8. Any edit after the ad-hoc run invalidates its evidence. Rerun after the true final edit.
9. Confirm cleanup in the same shell invocation (`rm`, disable the trap, then `test ! -e "$verify"`) before reporting that the temporary verifier was removed. A trap alone is not evidence of cleanup, and the shell's printed script path plus exit code should be retained in the final summary.

A successful final marker is useful only after every preceding command and runtime assertion is guarded by `set -e` and has genuinely passed.
