# Kanban + subagent workflow for web MVP builds

Use this reference when the user asks to build a full-stack/web MVP "using kanban and subagents" or similar.

## Pattern

1. Create a session kanban with `todo` before editing:
   - inspect project/boilerplate
   - seed/copy project
   - subagent core/domain libraries
   - subagent UI/integration
   - parent integration/build fixes
   - deploy/public verification
2. Dispatch parallel subagents only after the project shell exists. Give each subagent:
   - exact project path
   - package manager and test/build commands
   - scoped file ownership to reduce conflicts
   - product decisions from the PRD
   - TDD requirement for library/domain logic
3. Parent must re-read any files subagents report they changed before patching.
4. Parent owns final integration:
   - wire placeholder UI to real runtime/library behavior
   - update tests to reflect changed UX labels
   - run full test suite and production build
5. Parent owns deployment and public verification.

## Deployment verification notes

For projects served under `/projects/<slug>/`, verify the active nginx alias/root before copying build artifacts. In this environment, generic `/projects/` traffic is served from `/var/www/html/projects/`, while PRDs are served from `/usr/share/nginx/html/prds/`.

After deployment:
- `curl` local and public app URL for HTTP 200.
- `curl` referenced JS/CSS assets for HTTP 200.
- For SPAs whose `index.html` only contains a root div, grep the built/public JS bundle for visible app markers such as title text, runtime labels, or feature copy.
- Browser visual QA is useful but not a replacement for curl/build verification; if browser automation times out, report it as a limitation only after HTTP/assets are verified.

## Common pitfalls

- Do not stop with generated FFmpeg commands if the user asked to build the product; wire the UI to a real browser runtime or explicitly report what remains blocked.
- Avoid overlapping subagent scopes on the same large files when possible. If overlap happens, parent must reconcile and run the full suite.
- Vitest does not support Jest-only flags such as `--runInBand`; rerun the project-native test command before treating the test runner as failed.
