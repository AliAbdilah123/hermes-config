# Project media-source choice layout

Use when the Project workspace supports both local media and AI-generated media.

## Intent

Local upload and AI generation are alternative entry points into the same post workflow. Do not present generation as a mandatory stage above upload or bury upload inside the Posts editor.

## Recommended layout

- Start the workspace with one **Add media to this project** section.
- Present two equal cards separated by an explicit **or**:
  - **Upload your media** — finished local images/videos; each selected file becomes an unsaved draft.
  - **Create with AI** — opens the creation studio for prompt, output type, quantity, generated results, refinement, and selection.
- Keep both cards equal in hierarchy. A filled AI action is acceptable when generation is the richer flow, but copy must still make upload a complete alternative.
- Stack cards on narrow screens; use side-by-side cards on desktop.
- Keep the existing Posts section focused on destinations, draft editing, saving, and scheduling. Avoid a second duplicate project-level upload control there.

## Interaction boundary

- Hide prompt fields and generated-output history until the user explicitly opens the creation studio.
- Preserve completed/failed generation output behavior, retry controls, and conversion of selected outputs into local drafts.
- Upload should continue using the accessible label + hidden native file input pattern and retain drag/drop if supported.
- Opening or closing generation must not mutate existing drafts, selected destinations, or schedules.

## Verification

1. Before opening the studio, assert both source choices and the explicit “or”; prompt fields must be absent.
2. Open the studio and assert prompt/type/quantity controls appear.
3. Submit generation and verify the existing request payload remains unchanged.
4. With generated jobs loaded, open the studio before testing output selection/retry because results are intentionally hidden while closed.
5. Exercise local file selection and drag/drop from the new upload card.
6. Run focused workspace tests, typecheck, production build, and diff checks.
7. Visually inspect desktop and mobile for equal card heights, readable copy, no clipping, and unambiguous alternative-source hierarchy.

## Pitfalls

- A styled `<label>` that activates a file input is not exposed as a button role; tests should query its visible text or the input’s accessible label.
- Moving upload controls requires updating drag/drop tests to target the new card, not preserving obsolete copy solely for test compatibility.
- If generated outputs are conditionally hidden with the studio, existing output tests must open the studio first.
