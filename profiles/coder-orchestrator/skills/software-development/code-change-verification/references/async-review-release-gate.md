# Asynchronous review release gate

Independent review is a hard pre-release gate even when delegated in the background.

1. Dispatch review early enough to overlap with tests and other non-release work.
2. Do not commit, push, deploy, or report READY while the verdict is pending. “Dispatched” is not “passed.”
3. Evaluate every finding before release. For valid findings, add a failing regression test, apply the smallest fix, and repeat full verification.
4. If a verdict arrives after an incorrect completion claim, correct the record immediately, fix and redeploy, then publish fresh test, public E2E, commit, and push evidence.

This prevents a race where an implementation is released before its independent reviewer identifies a committed-write reconciliation bug, unsafe numeric boundary, authorization gap, or similar edge case.