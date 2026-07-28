# Role-scoped dashboard tabs and aggregate views

Use this pattern when adding or simplifying role-specific dashboard navigation, especially when existing pages and creation behavior must be exposed as sibling tabs rather than duplicated.

## Minimal implementation sequence

1. Trace every navigation surface: canonical routes, nested layouts, legacy redirects, sidebar/workspace navigation, visible tab strips, and route tests.
2. Put one shared nested layout beneath the role guard so every sibling page receives the same tab strip and authorization boundary.
3. Preserve existing overview/settings routes; add sibling routes for new tabs. Use exact matching on the overview link so child routes do not mark Overview active.
4. Reuse the existing feature component and creation behavior. A route-mode prop such as `available | create` is preferable to copying forms, validation, upload handling, or POST logic into new pages.
5. Keep list and create concerns visually separate: the list route renders all authorized records but no creation form; the create route renders the shared form but not the list. Navigate to the list only after successful creation.
6. For aggregate views, enforce actor scoping on the server. Resolve the authorized actor's domain membership ID, aggregate only assigned records, define inclusion/exclusion semantics explicitly, and return a narrow DTO.

## Focused tests

- Render the nested layout through real router routes; assert every preserved/new tab href, active-tab class, and child `<Outlet>` content.
- Test route modes directly: list mode shows every returned record and omits the form; create mode exposes shared fields and verifies the canonical POST path/payload.
- If image creation is staged (create entity, upload, patch), retain a focused test proving the entity ID is passed to upload and the resulting URL is patched.

## Verification ladder

- Run focused route/behavior tests first, then changed-file lint and the production build.
- If workspace verification does not recognize canonical commands, create an OS-safe temporary executable with `mktemp /tmp/hermes-verify-XXXXXX`, invoke it directly, and remove it afterward. Label this **ad-hoc targeted verification**, not suite-green evidence.
- Do not suppress a new lint finding. If a touched legacy file has a known pre-existing rule violation, run repository lint unchanged and report its failure separately; a changed-file lint may disable only that specific pre-existing rule while still checking all other rules.
- Run the broader suite when practical. If it fails outside the touched scope, report the unrelated failure precisely; do not repair unrelated debt without authorization.

## Dirty-worktree discipline

Record `git status` before editing. Stage only explicit feature files. Inspect the staged diff and run `git diff --cached --check` before committing so pre-existing modifications are neither overwritten nor accidentally shipped.
