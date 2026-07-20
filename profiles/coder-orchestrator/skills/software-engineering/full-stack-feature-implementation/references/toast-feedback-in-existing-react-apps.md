# Toast feedback in an existing React application

Use this pattern when adding operation feedback to an established frontend without replacing its action flows.

## Minimal implementation

- Add one toast value at the application boundary: `{ message, type: "success" | "error" }`.
- Render one shared toast component with `role="status"` and `aria-live="polite"` for success; use `role="alert"` and `aria-live="assertive"` for errors.
- Wrap async operations in a small helper that preserves the existing action, emits the exact success message only after completion, and includes the caught error detail in failure feedback.
- Wire existing archive, retry, copy, and invitation flows instead of creating parallel workflows.
- Validate invitation email at the submission boundary and use corrected user-facing copy.

## Test-first checks

1. Render success and error toasts and assert their live-region roles.
2. Run the async helper with resolving and rejecting actions; assert exact messages.
3. For clipboard feedback, assert that the full value is copied and success is emitted after the promise resolves.
4. Run the focused frontend suite, then the production build.

## Existing-worktree safety

Before delegation, inspect `git status` and tell the coding agent to preserve unrelated edits. Afterward, review only the touched diff and run `git diff --check`. If the frontend build copies assets into an embedded backend directory, include the generated asset replacement in verification and in the same feature commit.
