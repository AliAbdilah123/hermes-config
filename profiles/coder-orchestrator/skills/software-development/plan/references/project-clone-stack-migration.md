# Project Clone + Stack Migration Planning Reference

Use this reference when planning a project clone/migration where the target must run on the user's standard stack and remain isolated from other projects.

## Planning checklist

1. **Separate source import from target runtime**
   - Clone the source repo into a temporary/import path first.
   - Treat the source as read-only migration material unless the user explicitly asks to preserve it as the runtime.
   - Build the final target from the user's standard boilerplate/stack when that is the stated migration goal.

2. **Define isolation before implementation**
   - Target path, project name, service name, database path, ports, nginx route, public URL.
   - Explicitly state which existing projects must not be touched.
   - Include collision checks for existing directories, services, ports, and web routes.

3. **Preserve env variable names when requested**
   - Include a root `.env` and `.env.example` plan.
   - Keep original/source variable names as compatibility aliases.
   - Describe internal mapping rules (example: `DATABASE_PATH || file:DATABASE_URL`, `XENDIT_SECRET_KEY || XENDIT_SECRET`, `PUBLIC_BASE_URL || WEB_APP_URL`).
   - Ensure `.env`, runtime DBs, secrets, and build artifacts are ignored by git.

4. **Audit source before porting**
   - Inventory docs, routes/endpoints, schemas, pages, roles, background jobs/queues, payments, analytics, observability, and auth.
   - Mark every source feature as `port`, `replace`, or `defer`.

5. **Plan migration phases**
   - Bootstrap from target stack.
   - Config/env compatibility.
   - Database schema translation.
   - Backend API/domain port.
   - Frontend page/design-system port.
   - Deployment (service + web server) with isolated names.
   - Full validation and docs.

6. **Validation must be real**
   - Backend tests.
   - Frontend tests and production build.
   - Local health/API smoke tests.
   - Public URL health check.
   - Browser smoke test for primary user/admin flows.

## Recommended plan sections

- Goal
- Current context / assumptions
- Proposed approach
- Target directory layout
- Environment variable compatibility contract
- Isolation checks
- Step-by-step phased tasks
- Files likely to change
- Tests / validation
- Risks, tradeoffs, open questions
- Definition of done

## Common pitfalls

- Planning to run the cloned old stack directly when the user asked to migrate it to the current stack.
- Forgetting env compatibility aliases, which makes later secret updates harder.
- Reusing ports, services, database files, nginx locations, or process names from an existing project.
- Writing a plan that says "migrate backend" without enumerating schema, endpoints, auth/roles, payments, queues, and frontend pages.
- Calling a public link done without public health and browser checks.
