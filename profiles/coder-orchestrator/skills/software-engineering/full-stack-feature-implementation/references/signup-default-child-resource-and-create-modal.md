# Signup-created default child resources and homepage creation modal

Use this pattern when registration already creates a default tenant/workspace and a new required child resource (board, project, inbox, etc.) must also exist immediately.

## Backend

- Extend the existing registration transaction; do not make a second HTTP request after signup.
- Insert in dependency order: user → workspace/tenant → membership → required children.
- Check **every** `Exec`, `LastInsertId`, and `Commit` error. Roll back and return a controlled error if any default-resource insert fails; never return a successful account with a partially initialized workspace.
- Use the same schema/API-compatible defaults the normal create route would accept.
- Add a signup-boundary regression test: sign up, authenticate with the returned session, list the child resources, and assert the default child belongs to the default workspace.

## Frontend

- Reuse the existing creation dialog and submit path. The homepage CTA should only seed the minimum form state (for example, the first/default workspace ID) and open that dialog.
- Label the CTA by its action, such as **Create Board**, rather than using a destination noun like **Board**.
- If multiple workspaces are possible, keep the workspace selector in the modal; preselect a sensible default rather than silently binding creation to the current page.

## Verification

1. Run the focused signup regression test and watch it fail before implementation.
2. Run the full backend suite and frontend tests/build.
3. Rebuild embedded frontend assets before compiling/restarting the backend.
4. After restart, use a bounded readiness retry before checking HTML and bundle markers; `systemctl is-active` can become true just before the listener accepts connections.
5. Verify the public page references the new asset hash and the deployed bundle contains the new CTA label.
