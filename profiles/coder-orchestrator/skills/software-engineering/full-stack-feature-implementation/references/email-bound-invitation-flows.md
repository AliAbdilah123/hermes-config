# Email-bound workspace invitation flows

Use this pattern when invitations must work for existing accounts, invite links, and newly registered users.

## State and trust boundaries

- Treat the normalized invitation email as the identity boundary; never accept an invitation merely because a user possesses its URL/token.
- Return only active, unexpired invitations for automatic prompts. Keep accepted invitations queryable so the UI can render a terminal “Already accepted” state.
- Enforce acceptance authorization on the backend even when the client disables the action.
- Reuse the application’s existing invitation, authentication, notification, and modal workflows rather than creating parallel state.

## Existing-account flow

1. Creating an invitation should produce an invitation notification for an account already using that email.
2. The notification action opens the existing invitation modal.
3. Pending invitation: enabled action labeled exactly “Accept invitation”.
4. Accepted invitation: disabled action labeled exactly “Already accepted”.

## Invite-link session handling

1. Resolve enough invitation metadata to compare its normalized email with the authenticated session.
2. Matching email: open the invitation modal.
3. Different email: preserve the invite destination through the established return-path mechanism, terminate the mismatched session, and redirect to login.
4. Do not expose acceptance merely because the session is authenticated; email identity must match.

## Registration and first-login flow

- After account creation/login, discover active invitations for that normalized email and expose their notifications.
- Automatically open the invitation modal once on the first authenticated visit. Persist or consume the auto-open marker server-side or through an existing durable state pattern so refreshes do not reopen it forever.
- Expired invitations must neither notify nor auto-open.

## TDD coverage

Write failing tests first for:

- Existing account receives a clickable invitation notification.
- Pending and accepted modal labels/disabled states.
- Matching invite-link session opens the modal.
- Mismatched session is logged out and redirected to login with return flow preserved.
- New account receives active invitation notification and one-time auto-open.
- A second active-invitation lookup does not auto-open again.
- Expired invitation is ignored.
- Backend rejects acceptance by a nonmatching account.

Run focused backend and frontend tests, then their full suites and the production frontend build. If frontend assets are embedded into the backend, verify the build copied the new hashed assets and updated the embedded index before committing.