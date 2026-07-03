# PRD bounty/gig marketplace into an existing Go + Vite app

Use when a PRD asks for a bounty/gig marketplace feature in an app that already has older job/proposal concepts.

## Durable lessons

1. **Do not assume a clean schema.** Search existing models/handlers/tests for `proposal`, `quota`, `bank`, `verified`, `open_call`, and old job status terms before adding new bounty tables. Existing tables may already use the same names with different columns.
2. **Avoid table-name collisions.** If an old `proposals` table exists for `jobs`, either migrate it to a superset schema or use a distinct table name for new bounty proposals. Two `CREATE TABLE IF NOT EXISTS proposals...` statements silently keep the first shape, then later inserts fail with `no column named ...`.
3. **SQLite additive migrations need column guards.** For in-place local apps, add an `ensureColumn(table, col, def)` style helper and run it after `CREATE TABLE IF NOT EXISTS` so existing live DBs gain new fields.
4. **Go JSON tag pitfall:** grouped struct fields such as `Title, Description string `json:"title","description"`` do not create separate JSON names. Use one field per JSON tag for request bodies, especially for tests that post snake_case keys.
5. **Keep legacy endpoints compatible while adding PRD endpoints.** If old UI/tests still hit `/jobs/open-calls` or `/proposals/:id/approve`, preserve those routes unless the user explicitly wants a breaking replacement. Add `/bounties` in parallel, then adapt frontend incrementally.
6. **Verification gate on live seed data:** seeded/demo users in older DBs may lack new `email_verified_at`; expose resend/verify routes and use them in smoke tests instead of assuming existing users are verified.

## Verification checklist

- Backend tests cover unverified post/proposal rejection, invalid duration, bank-details requirement, over-quota confirmation, and decline+reopen.
- Frontend build/test still pass after route additions.
- After deploy, smoke both backend behavior and deployed bundle markers for user-facing concepts (`Bounty`, `Bank details`, Rupiah/quota/duration copy).
