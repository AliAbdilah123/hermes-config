# Sidebar context moves and public release verification

Use this checklist when moving account/workspace controls from a header into responsive navigation.

## Behavioral coverage

- Assert the controls are absent from the old header region.
- Open the mobile navigation and scope assertions with `within(sidebar)`; desktop and mobile copies may coexist in the DOM.
- Verify signed-in display name, username/role, selected tenant, and allowed tenant options.
- Exercise search by typing a tenant fragment and asserting matching options remain while non-matches disappear.
- Preserve authorization: tenant users see only assigned tenants; global users retain the aggregate option and all authorized tenants.
- Verify a newly created tenant appears immediately in the relocated selector.

## Accessibility pitfalls

- Give desktop and mobile control copies unique IDs. Reusing IDs makes labels resolve to the wrong hidden control.
- Do not nest a design-system `Label` inside a native `<label>` wrapper. Prefer a neutral `<div class="field">` containing one `Label` and its control.
- Keep explicit `htmlFor`/`id` association and test with `getByLabelText` or role/name queries.

## Release sequence

1. Run the focused regression test and confirm RED before implementation.
2. Run focused tests, typecheck, lint, full tests, backend tests, build, and `git diff --check` as applicable.
3. Commit and push only the intended files; leave unrelated untracked files untouched.
4. Deploy the built artifact and restart the service.
5. Poll the local health endpoint after restart rather than assuming `systemctl is-active` means the socket is ready.
6. Read project deployment metadata for the canonical public host/path. Do not infer it from an old script default.
7. Check public health and run public E2E against an explicit canonical URL override when the script supports one.
8. Report READY only after public E2E passes.
