# Auth + workspace isolation plan-first workflow

Use this when a local Go + SQLite + React/Vite app has workspace/project tables or membership tables but no real authenticated session boundary, and the user asks to prevent permission mixing across workspaces.

## Pattern

1. **Inspect before coding**
   - Locate backend/frontend, service/nginx/public URL, schema, and current workspace/project route shape.
   - Check whether membership tables already exist but are unused. Do not assume their presence means access control is enforced.
   - Identify every route that accepts a workspace/project ID from the client and verify whether it joins through membership.

2. **Publish the review artifact first**
   - For this user, create a styled public HTML review/implementation plan before touching live behavior unless they explicitly asked to implement immediately.
   - The artifact should name the current gap plainly: e.g. routes expose all workspaces/projects by raw IDs, no signed-in user/session gate.
   - Include the minimal backend/frontend/test/deploy plan and a public link.

3. **Smallest safe implementation plan**
   - Add `auth_users` and `auth_sessions` in the same SQLite DB.
   - Registration creates user + private workspace + `owner` membership in one transaction.
   - Session middleware derives user ID, tenant/workspace access, and role from persisted membership.
   - `GET /workspaces` returns only joined workspaces.
   - `POST /workspaces` writes owner membership transactionally.
   - Project/diagram read/write routes verify the project workspace is joined by the session user; return controlled 403/404 for non-members.
   - Frontend adds compact sign-in/sign-up and token/cookie-aware API helper.

4. **Verification to require after approval**
   - Backend tests: signup, signin, owned workspace creation, cross-user workspace/project/diagram denial, seeded/default data backfill if applicable.
   - Frontend test/build: auth form/session flow and workspace loading from authenticated API.
   - Public smoke: sign-up and session lookup via public nginx path; do not print tokens.

## Pitfalls

- A `workspace_members` table without auth/session lookup is only schema decoration; it does not isolate data.
- Do not let handlers infer workspace access from request body/query/path alone. Access must come from session user membership.
- Do not implement live behavior from a bare request if the user's standing workflow preference is plan/review first; stop after publishing the review artifact and wait for approval.
