# Account lifecycle timing changes

Use this checklist when changing the account-deletion grace/recovery window.

1. Write or update the behavior test first and confirm it fails against the old duration.
2. Change the single backend grace-period source used to calculate both proposed and committed deletion deadlines.
3. Update deadline assertions and sign-in `remainingDays` boundary assertions; rounding may legitimately report either the nominal day count or one less.
4. Update user-visible copy in authenticated account settings and restoration errors.
5. Update public legal/privacy/deletion guidance in every supported language.
6. Search application source for old phrases such as `30-day`, `30 days`, and localized equivalents. Inspect matches rather than replacing globally: analytics ranges, session expiry, token cleanup, billing periods, and dispute windows are unrelated.
7. Run targeted backend lifecycle tests, targeted frontend settings/restore/legal tests, and the frontend production build.
8. Run the broader backend suite. If unrelated tests fail, report them separately and retain fresh passing evidence for the lifecycle scope.
9. Keep pre-existing database files, plans, generated docs, and unrelated dirty work out of the commit by staging only task-owned paths; verify the cached diff before commit/push.

The deletion worker already uses persisted `delete_at`; changing the source deadline affects newly requested deletions without rewriting existing pending operations unless migration is explicitly requested.
