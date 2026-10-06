# Dirty worktrees and partially red suites

## Preserve and attribute changes

When unrelated changes already exist, capture `git status --short` and focused diffs before editing. Treat that snapshot as an ownership boundary.

- Patch only intended hunks; never reset, checkout, clean, or rewrite a pre-dirty file wholesale.
- Inspect the pre-task diff of any required file that is already modified and preserve those hunks.
- Derive the task's exact changed-path list from edits actually made, not from final `git diff --name-only`, which includes unrelated dirt.
- Report a required pre-dirty path as “touched by this task but already dirty”; list other dirty paths separately as preserved.

## Verify in layers

Run focused tests first, then broad suites and builds as separate commands. If a broad suite fails outside the changed area:

- Keep and report focused passing evidence.
- Run independent builds separately so shell chaining does not suppress them.
- Report exact failing test names and assertions.
- Say “outside the changed scope” unless baseline evidence proves the failure was pre-existing; do not infer provenance merely because focused tests pass.
