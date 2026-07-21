# Standalone Settings Page Shell Parity

Use when a Settings section has a dedicated route/component (for example a durable Notification Center) instead of rendering through `SettingsPage.tsx`.

## Root cause pattern

A dedicated route can bypass the Settings shell even though it visually belongs to Settings. This causes drift such as:

- missing horizontal quick navigation on mobile or desktop;
- a centered/narrow content column while other Settings pages are left-aligned;
- inconsistent active-state, width, padding, header, or back behavior.

## Minimal implementation pattern

1. Inspect `App.tsx` route precedence. A dedicated route such as `/app/settings/notifications` may render `NotificationsPage` before `/app/settings/:section` can render `SettingsPage`.
2. Extract shared Settings navigation configuration and UI into one reusable component rather than copying seven buttons into the standalone page.
3. Render the shared quick menu before standalone page content, mark the current section with `aria-current="page"`, and route other items to `/app/settings/:section`.
4. Match the standard Settings content shell exactly. Current desktop geometry is left-aligned `max-w-[1040px]` with `p-4 md:p-8`; do not use `mx-auto max-w-4xl` unless the approved design explicitly calls for a centered page.
5. Preserve the standalone feature's data flow, mobile header/back behavior, bell, filters, actions, and detail routes.

## Regression coverage

Add focused assertions that:

- the Settings navigation exists before the page's primary content;
- the current section is active;
- clicking another section navigates correctly;
- the main wrapper uses the shared width/padding and does not include centering classes.

Then run the standalone page test, Settings page test, shared navigation/bell tests, typecheck, and production build. Verify the deployed standalone chunk and shared-navigation chunk return `application/javascript`.

## Dirty-worktree safety

When delegating in a clean worktree, create the worktree in one command first, then launch the coding agent in a separate tool call whose `workdir` is that new path. A tool call's working directory is resolved before its shell command runs, so creating and entering a not-yet-existing worktree in the same call can accidentally leave the agent operating in the dirty primary checkout. Independently confirm the agent's reported workdir and inspect the clean worktree diff before deployment.
