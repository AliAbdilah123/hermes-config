# Notification Settings: History-First Handoff

Use when implementing an approved Settings hierarchy where durable notification history must be primary and delivery preferences secondary.

## Minimum production change

- Keep the existing notification list, search, filters, grouping, pagination, row actions, routes, API calls, and shared bell unchanged.
- Render the Notification Center/history section first and visible by default.
- Move the existing preferences component to the final section and wrap it in native `<details>/<summary>` labeled `Notification Settings`.
- Leave `<details>` without `open` so preferences start collapsed; use the native control for keyboard and disclosure semantics.
- If the preferences component already owns a card shell, flatten only that immediate nested shell with scoped child selectors rather than rewriting the component.
- Add only the disclosure icon needed by the summary; mark it `aria-hidden` and rotate it from the parent `group-open` state.

## Focused regression shape

A single page test should prove:

1. The Notification Center heading precedes the preferences content in DOM order.
2. The enclosing `<details>` has no `open` attribute initially.
3. A known preference control exists but is not visible while collapsed.
4. Clicking the `Notification Settings` summary opens the disclosure and makes that control visible.
5. Existing preference interaction tests expand the disclosure before querying or clicking toggles.

Keep the shared Notification Bell test in the focused suite to prove the explicitly out-of-scope dropdown did not regress.

## Dirty-worktree delivery

When the main checkout contains unrelated work, create a detached worktree from current `HEAD`, apply only the reviewed feature patch, install from the lockfile, and rerun focused tests, typecheck, and build there. Deploy that clean `dist/`, verify the distinctive page chunk and public JavaScript content type, then commit only the scoped files and push the detached commit to the intended branch.

Before doing this, confirm the approved feature does not depend on uncommitted shared changes; a clean worktree intentionally excludes them. Never reset, stage, or commit unrelated files in the original checkout.
