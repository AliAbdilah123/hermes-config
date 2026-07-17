# Media editing and Google Sign-In interaction fixes

Use this reference when implementing or regressing the combined media-editor and app-login interaction fixes from the approved SocialZen review.

## Video trim handles

The visible timeline handles must be directly draggable, not merely decorative overlays above hidden range inputs.

- Capture the pointer on `pointerdown`.
- Track whether the start or end handle is active.
- Convert `clientX` against the timeline track bounds into a duration value.
- Preserve the minimum trim duration (`start <= end - 1`, `end >= start + 1`).
- Keep the hidden/native range controls for keyboard accessibility.
- Add a component test that drags the visible handle and asserts the displayed trim state changes.

## Crop queue invariant

In Create Post, the active crop file and the remaining queue must be disjoint. When accepting files:

```ts
const [first, ...rest] = allowed
setPendingFile(first)
setCropQueue(rest)
```

Do not store `allowed` wholesale in the queue while also assigning `first` as active; that duplicates the first upload/crop item.

## Removing completed replacement media

Edit and Edit & Retry must allow removing one already-uploaded replacement item without resetting all media.

- Render each completed thumbnail in a positioned wrapper.
- Add a `type="button"` X control with an explicit accessible label such as `Remove uploaded media 1`.
- Remove by index with an immutable filter.
- Key by the stable upload key (`r2Key`) rather than array index when available.
- This action is distinct from crop-modal Cancel, which restores previous media according to the existing retry workflow.

## Google GIS concurrency guard

Multiple rapid clicks on Google Sign-In must share one in-flight GIS attempt. Keep a module-level active promise:

```ts
let activeSignIn: Promise<Result> | null = null

export function signInWithGoogle() {
  if (!activeSignIn) {
    activeSignIn = startGoogleSignIn().finally(() => { activeSignIn = null })
  }
  return activeSignIn
}
```

The guard must clear on both success and failure so later attempts can retry. Test that concurrent calls return the same promise/flow and initialize GIS once.

## Backend scope check

Before changing backend Google auth, inspect whether JWKS caching and token verification are already implemented. If the approved problem is already solved, leave backend code untouched and verify with targeted Google tests plus `go build ./...`.

## Verification and delivery

Run focused frontend tests first, then typecheck and production build. Run targeted Google backend tests and a full backend build. If only frontend files changed, deploy only the frontend. Verify the public page is 200, the current JS asset is `application/javascript`, and a distinctive new bundle marker exists. Commit only the implementation/test files; do not accidentally stage unrelated untracked PRD/plan artifacts.
