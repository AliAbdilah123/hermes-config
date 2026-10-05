# Native file drop area for an existing file picker

Use this for a focused request to turn an existing upload button/input into a drop area without changing the upload pipeline.

## Minimal implementation

1. Reuse the existing file-processing function for both `input.onChange` and `drop.dataTransfer.files`.
2. Keep the native `<input type="file">` in the DOM. Visually hide it and wrap it with a styled `<label htmlFor>` so clicking and keyboard-driven file selection still work.
3. Add `onDragOver={event => event.preventDefault()}` or the browser will not permit dropping.
4. In `onDrop`, call `preventDefault()`, honor the existing disabled/busy state, and pass `event.dataTransfer.files` into the same handler.
5. Preserve `multiple`, `accept`, and the input's accessible name. If the label's new instructional copy breaks an established exact accessible-name contract, add an explicit `aria-label` to the input.

## Focused check

Add one interaction test that fires `drop` with a `dataTransfer.files` array and verifies the normal downstream UI result. Keep the existing file-input change test; together they prove click selection and drag/drop converge on the same path.

## Dirty repository delivery

For a focused current-branch change, inventory status first, modify only the owning source and focused test, stage exact paths, inspect/check the cached diff, then commit and push without touching unrelated tracked or untracked files. Verify local `HEAD` equals the upstream SHA after push.
