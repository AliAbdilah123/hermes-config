# Generated UI component verification

Use when a component registry CLI (for example shadcn) generates files in an existing frontend.

1. Run the project-local generator for the requested component rather than hand-copying an approximation.
2. Immediately inspect `git status` and dependency-manifest/lockfile diffs. Generators may update unrelated package versions; revert incidental changes unless the generated component requires them.
3. Import the generated primitive through the repository's established UI-component path and preserve existing action handlers and destructive semantics.
4. Add one focused regression check that proves the menu trigger and each action remain wired to the original handlers.
5. Run, in order, the repository test command, static/type check, production build, and `git diff --check`.
6. Ensure the project changelog records the user-visible change when the repository requires implementation logging.
7. Stage only task files; never sweep unrelated untracked runtime data, plans, backups, or generated local artifacts into the commit.

Report only fresh results from these commands. A successful generator run is not verification.
