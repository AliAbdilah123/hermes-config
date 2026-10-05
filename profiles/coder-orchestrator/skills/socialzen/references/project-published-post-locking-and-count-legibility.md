# Project count legibility and published-post locking

Use this when project cards have unreadable post counts or project detail exposes published posts as editable.

## Project-card status text

- Do not use a generic muted token without checking its computed contrast on the actual card/theme; it may resolve to white or near-white.
- Use an established readable semantic foreground token (for example `--ink-2`) for metadata such as `{n} posts`.
- Keep the status dot independent from the text color.
- Regression-test the class on the element that owns the text color; the exact text may be inside a child `<span>`.

## Published child posts

Treat `PUBLISHED` as immutable in the project workspace:

- Derive one `published` boolean per post.
- Disable every content-changing control: title, post type, file input, media reorder/remove, comments toggle, caption, and any equivalent future field.
- Keep non-mutating affordances such as expand/collapse available.
- Do not rely only on disabled UI. The shared project save loop must exclude published posts so it cannot PATCH them or accidentally submit `status: "DRAFT"`.
- Local/unsaved posts remain saveable; preserve existing behavior for drafts and scheduled posts unless requirements say otherwise.

## Verification

Add a focused component test that:

1. Loads a project containing a `PUBLISHED` child.
2. Asserts representative controls are disabled.
3. Clicks the project save action.
4. Asserts the project-level PATCH still occurs if appropriate, but no post PATCH is sent for the published child.
5. Checks project-count metadata uses the readable foreground class on the actual class-owning parent.

Then run the focused test, typecheck, production build, deploy the generated frontend artifact, restart the application service when required by the project workflow, and verify the public authenticated routes.