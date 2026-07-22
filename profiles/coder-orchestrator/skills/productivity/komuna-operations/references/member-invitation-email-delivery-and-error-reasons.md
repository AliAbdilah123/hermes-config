# Member invitation email delivery and failure reasons

Use this when implementing or debugging program-member invitations in Komuna's Go + SQLite API and React admin UI.

## Domain contract

An invitation may be sent only when the email belongs to a registered Komuna user who is not currently active/pending in the target program and is not banned. A former member (`left` or inactive) is eligible. A pending invitation remains valid for 24 hours.

A repeated request during that 24-hour window is idempotent: return the existing invitation and do not send another email. After expiry, create and send a new invitation.

The acceptance endpoint must bind the token to both program and normalized recipient email, reject expired/used tokens, allow eligible former members to rejoin, and atomically mark successful acceptance.

## Backend response codes

Return stable, short machine codes from the API so the frontend can explain failures:

- `user_not_registered`
- `user_already_in_program`
- `user_banned`
- `email_not_configured`
- `email_delivery_failed`
- token flow: `invitation_not_found`, `invitation_recipient_mismatch`, `invitation_expired`, `invitation_already_used`

If email delivery fails after inserting an invitation, remove or invalidate that invitation so a retry is not suppressed by idempotency. Audit the provider failure without exposing provider details to the user.

## Frontend pitfall

Do not replace all API failures with one generic “Failed to send invitation” message. `ApiClient` already preserves the API error code in `Error.message`; map known invitation codes to concise localized reasons and retain a generic fallback for unknown/network failures.

Example display: `Invite failed: User is already in this program.`

Keep English and Indonesian locale keys in sync.

## Regression matrix

Test at least:

1. Registered user with no membership: sends once.
2. Former `left`/inactive member: sends once.
3. Active or pending member: blocked, no email.
4. Banned member: blocked, no email.
5. Unregistered email: blocked, no email.
6. Duplicate request before expiry: same token/record, no second email.
7. Request after expiry: new token/record and email.
8. Wrong recipient, expired token, reused token: acceptance rejected.
9. UI renders a short localized reason for a known API error code.

## Verification

Run the focused Go invitation tests, the focused Members page failure-reason test, and the frontend build. If the environment requires explicit verification evidence, create an OS-safe temporary script with `mktemp /tmp/hermes-verify-member-invite-XXXXXX.sh`, run the focused checks, inspect the built bundle for a representative reason string, and remove the script afterward. Report this accurately as ad-hoc targeted verification rather than claiming the entire suite is green.
