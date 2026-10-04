# Correcting a rejected UI migration

Use when review finds that a supposed full UI revamp is mainly a wrapper, global recoloring, or duplicated legacy hierarchy.

## Correction sequence

1. Re-read the acceptance plan and reviewer findings; enumerate every named surface, including route-level early returns, dialogs, loading/error/empty states, account, notifications, badges, and toasts.
2. Write interaction tests first and retain exact RED output.
3. Make async navigation transactional: load destination prerequisites before committing view/history; route rejection through existing error/toast behavior; no-op on the active canonical destination.
4. Use the installed accessible dialog primitive for mobile drawers. Test focus containment, background isolation, scroll lock, Escape/backdrop dismissal, and opener-focus restoration.
5. Put actual controls in shell breadcrumb/action/account slots. Remove duplicate legacy navigation instead of nesting it inside the new shell.
6. Mark each distinct screen with explicit scoped surface structure/classes. Shared tokens and global recoloring are not evidence that every surface migrated.
7. Preserve inspector-versus-page roles and all API/state behavior; omit unsupported prototype data.
8. Replace colliding broad `header`/`nav` overrides with scoped shell/surface rules. CSS source-string assertions do not prove responsive geometry or overflow.
9. Run focused GREEN, full tests, build, and `git diff --check`.

## Verification evidence

If workspace automation still requires fresh evidence after canonical commands, create an OS-safe temporary script with `mktemp /tmp/hermes-verify-XXXXXX.sh`, run focused behavior tests plus build and `git diff --check`, remove the script, and label the result **ad-hoc targeted verification** rather than full-suite green.

## Test durability

When visual wrappers change, update old assertions only after confirming they encode obsolete structure. Prefer semantic assertions—landmarks, accessible names, route/action behavior—over exact class strings. Never weaken preserved behavior merely to make the migration pass.
