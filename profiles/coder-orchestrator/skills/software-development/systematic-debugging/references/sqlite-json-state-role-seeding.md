# SQLite JSON-State Role Seeding and Access Verification

Use when a project stores auth users in SQLite tables but app/domain state in a single JSON blob (for example `app_state.payload`) and the user asks to revoke/seed roles, memberships, or demo access.

## Durable lessons

1. **Inspect both layers before changing access.** Count/inspect auth tables (`auth_users`, `auth_sessions`) separately from the JSON state (`Programs`, `Members`, `Roles`, etc.). A displayed role or count may come from the blob, not normalized tables.
2. **Preserve existing auth identities.** When seeding many users, upsert/retain existing `auth_users` by email/id where possible, then assign them to programs in the JSON state. Do not treat newly seeded fixture users as a reason to discard real existing users unless explicitly requested.
3. **Remove automatic demo-admin fallbacks.** If users appear to become admin automatically, search for fallback workspace code that grants admin/superadmin roles when unauthenticated/default/dev user state is used. Fix that source, not just the seed data.
4. **Use role verification, not assumptions.** After seeding, verify role counts from state and through the real `/me/workspace` endpoint with signed-in seeded users:
   - intended manager user has only `member`/`manager` roles;
   - ordinary users have no `admin`/`manager` roles;
   - exactly one superadmin is marked as such;
   - no unexpected `admin` assignments remain.
5. **Back up before mutating blob state.** Copy the SQLite DB before rewriting `app_state.payload`; one malformed JSON update can corrupt the whole app fixture.
6. **Rebuild/restart if access logic code changed.** Data changes alone are insufficient when the bug is code-level fallback access. Rebuild the service binary and restart/relaunch the running process, then verify the live API.

## Minimal verification checklist

- DB backup path recorded.
- Auth users count equals target count.
- Program/member/session fixture counts printed.
- Role aggregate shows zero unintended admin assignments.
- Public/local health endpoint returns OK.
- `/auth/sign-in` works with the shared seeded password for representative users.
- `/me/workspace` confirms intended roles for manager, ordinary member, and superadmin accounts.
