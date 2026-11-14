# Progressive disclosure in create/edit forms

For small form-reordering requests, prefer native `<details>`/`<summary>` over new component state when its behavior and styling suffice.

1. Confirm create and edit share the same form.
2. Keep essential fields visible in the requested order.
3. Move every subsequent optional field into one disclosure region; put the specifically requested first hidden field at its top.
4. Keep save, cancel, and delete actions outside the collapsed region.
5. Preserve field state and submission wiring; this should usually be a JSX-only layout change.
6. Format the edited file, run the owning frontend's typecheck/build, and inspect a path-scoped diff so unrelated dirty-tree changes are not reported as task output.

Use a custom controlled disclosure only when product requirements exceed native behavior.