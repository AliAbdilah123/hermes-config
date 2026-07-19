# Small frontend changes in a dirty working tree

Use this when a minor UI request lands in a repository with unrelated local edits.

## Safe sequence

1. Record `git status --short`, branch, recent commits, and per-file diff stats before editing or delegating.
2. Give the coding agent an explicit ownership boundary: smallest diff, preserve dirty changes, no formatting, no commit/push/deploy.
3. After delegation, compare the changed-file set and diff size against baseline. Treat whole-file reformatting or unrelated backend/test edits as scope failure even if tests pass.
4. Restore only task-owned files to baseline, then reapply the minimal semantic patch. Never reset or checkout unrelated dirty files.
5. Avoid whole-file Prettier/formatters for a one-line JSX change; they can turn a tiny change into hundreds of lines and contaminate the commit.
6. Run the project-native frontend build/tests. If a pre-existing test fails because of unrelated dirty work, report it separately and still prove the scoped build.
7. For embedded frontends, rebuild assets before the backend binary, restart the actual system service, and verify the service's configured address/path rather than guessing localhost ports or root routes.
8. Before commit, inspect `git diff --check`, `git diff --stat`, and especially `git diff --cached --stat` after staging. Stage only owned source and generated embedded assets.
9. Check `git remote -v` before promising push. If no push destination exists, commit locally, report the blocker plainly, and do not claim source delivery.

## Key pitfall

A successful build does not validate scope. The primary guard for tiny dirty-tree tasks is a small staged diff that contains only the requested behavior plus required generated assets.
