# Surgical commits in a dirty worktree

Use when the requested change touches a file that already contains unrelated, uncommitted work.

## Goal

Commit only the requested hunk without reverting, formatting, or accidentally staging the user's existing edits.

## Procedure

1. Inspect `git status`, the full worktree diff, and the target hunk before editing.
2. Make the smallest worktree edit possible.
3. Stage clean files normally.
4. For a mixed target file, first try an index-only patch with `git apply --cached`.
5. If patch context fails because the worktree and `HEAD` differ substantially, synthesize the intended staged file from `HEAD`:
   - Read `git show HEAD:path/to/file`.
   - Assert the exact old fragment occurs once.
   - Replace only that fragment in memory.
   - Write the result as a Git blob with `git hash-object -w --stdin`.
   - Stage it with `git update-index --cacheinfo <mode>,<blob>,<path>`.
6. Run `git diff --cached --check` and inspect `git diff --cached` before committing.
7. Verify the worktree still contains all unrelated edits after the commit.

## Safety constraints

- Never use `git add <mixed-file>` when unrelated edits are present.
- Never reset, checkout, stash, or overwrite the user's dirty work to simplify staging.
- The uniqueness assertion is mandatory; abort if the old fragment is absent or duplicated.
- Build/test the worktree first, then separately verify the staged diff accurately represents the requested commit.
- If push reports no upstream, retry with `git push --set-upstream origin <current-branch>`; this is normal branch setup, not a reason to change branches.
