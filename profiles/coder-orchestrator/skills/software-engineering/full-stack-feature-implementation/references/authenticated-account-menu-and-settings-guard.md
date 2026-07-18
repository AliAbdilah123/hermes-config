# Authenticated account menu and settings guard

Use this pattern when a small React/Vite app needs a logged-in avatar menu and settings must remain private.

## Minimal implementation

1. Reuse the existing current-user response and logout/settings actions; do not add a second auth state.
2. Use native `<details>/<summary>` for a dependency-free avatar dropdown when its interaction is sufficient.
3. Render an avatar initial from the current email/name, then show the available display name and full email in the menu.
4. Keep Profile, Settings, and Sign out inside the menu. Reuse an existing dialog system when the app has no router or dedicated profile route.
5. Treat hidden UI only as presentation. Protect the settings API with the existing server auth middleware and add a logged-out request regression test expecting `401 Unauthorized`.
6. Check narrow-header placement: keep the avatar visible while secondary navigation wraps below it, and constrain the dropdown width to the viewport.

## Verification

- Run the project-native frontend tests and production build.
- Run backend tests, including the unauthenticated settings assertion.
- Exercise both states: logged out shows no account/settings UI and `/api/settings` returns 401; logged in opens the menu and each action works.
- For an embedded Vite frontend, rebuild assets before rebuilding/restarting the backend binary.
- Verify the deployed bundle/UI, then commit and push.

## Reporting pitfall

Do not report the feature as implemented or imply the public link contains it when edits were not built, exercised, and deployed. If execution is blocked, report the changes as unverified local edits and clearly state that the live app was not updated.