# Targeted UI CSS changes in a dirty workspace

For a small selector-specific spacing or styling request:

1. Inspect the selector and nearby cascade before editing.
2. Prefer one narrow override after the shared base rule (for example, a modifier setting only `padding-top: 0`) rather than changing the shared rule.
3. If the file already contains unrelated edits, stage only the new hunk. Review `git diff --cached` before committing so existing work is not captured.
4. Run the canonical frontend build when available.
5. Also leave fresh, focused verification evidence for the requested behavior. A temporary script created with `mktemp /tmp/hermes-verify-...` can assert that the exact override exists once and follows the base declaration; remove it after execution.
6. Report this accurately as “ad-hoc targeted verification,” not as the whole test suite passing.

Visual approval and automated verification are separate: defer broad UI tests during active design iteration, but perform focused verification immediately before commit/final completion.