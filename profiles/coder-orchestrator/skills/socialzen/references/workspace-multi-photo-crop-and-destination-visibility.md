# Workspace multi-photo crop and destination visibility

Use when changing SocialZen’s shared Project/Regular Post composer, cropper, or destination status surfaces.

## Product boundary

- A Project workspace may accept multiple photos (up to the provider/product limit). If the user starts with Photo and adds a second image, promote the effective post type to carousel semantics rather than silently discarding files or requiring a manual type switch.
- A Regular Post may retain its single-destination/single-photo constraint when that is the explicit product contract.
- Returning from Review must preserve editor state, including platform/account choices, while clearing the reviewed payload, reviewed targets, warnings/diffs, and other snapshot-derived state. Any changed destination requires a fresh preflight.
- Project cards and details must show destination identity and each target’s real lifecycle state, not only the parent status. Map known states explicitly (`DRAFT`, `REVIEW_REQUIRED`, `SCHEDULED`, `UPLOADING`, `PUBLISHING`, `PUBLISHED`, `FAILED`, `CANCELED`).

## Crop geometry rules

1. Derive recommended/allowed presets from the complete selected-platform set. Initialize a cross-platform image with a preset that is valid for every selected destination (normally 1:1 when Instagram and Facebook overlap).
2. Keep stable image/visible-content bounds separate from the mutable crop box.
3. On every preset switch, fit the new ratio against those stable bounds and use the previous crop only for its center. Never fit the next ratio inside the previous crop box; that causes cumulative shrinking.
4. Preserve crop state by exact `File` identity and only persist after that exact file has loaded.
5. Freeform means unlocked handles. Custom W:H means freeform mode with a temporary ratio lock; persist that lock with the file’s crop state.
6. Allow custom crops in the workspace, but validate provider compatibility at preflight/API boundaries. For Instagram feed images, reject ratios outside 4:5–1.91:1; for image carousels, require matching ratios within a small rounding tolerance.
7. Carry output width/height from upload response into the preflight payload so backend validation evaluates the generated crop, while allowing legacy media without dimensions to remain provider-validated at publish time.

## Edit-page destination/account parity

- Hydrate editable platform and account selections from the post’s target rows, not from a legacy single-account field. Keep platform selection and account selection synchronized: disabling a platform clears its selected accounts.
- PATCH target changes as desired replacement state. Validate every account belongs to the current user before the transaction, then atomically replace `post_targets`; preserve the parent lifecycle (`DRAFT` targets stay draft, scheduled targets stay scheduled) and refresh compatibility fields only when they exist.
- When saving a Project version, snapshot the newly supplied destinations rather than reusing the previous version’s `destinations_json`; otherwise edit appears successful but later hydration silently restores stale targets.
- Cards and details are separate surfaces. Render unique platform tags plus associated account/page names on both; reuse target-aware labeling so published and scheduled rows expose the same identity contract.

## Minimal implementation shape

- Reuse the existing cropper, queue, `WeakMap<File, CropState>`, media requirements, preflight, and `post_targets`; add no crop dependency or parallel workspace model.
- For edit-page multi-image replacement, pass the whole image queue into the existing batch cropper, expose its in-modal Add callback, and keep selectable/removable thumbnails in that single modal session. Do not reopen one modal per file.
- Keep media-limit and effective-post-type decisions in small pure helpers with focused tests.
- Show Freeform whenever custom cropping is enabled, even when recommended presets are supplied.
- Batch crop validation may relax “must equal a recommended preset” when custom ratios are allowed, but must retain same-ratio locking where the target carousel requires it.

## Verification

- Regression: cycle 1:1 → 4:5 → 1.91:1 → 1:1 and assert the final box equals the first box.
- Regression: adding image 2 to a Project Photo promotes it to carousel and preserves all files in order.
- Regression: Back to editor clears reviewed snapshot state and destination controls remain editable.
- Regression: Edit hydrates all current platforms/accounts, changing one account PATCHes replacement targets, and the next Project-version snapshot contains those new destinations.
- Regression: selecting two replacement photos opens one crop session containing both thumbnails and an in-modal Add action.
- Regression: cards/details render every unique platform tag, associated account/page name, and target status.
- Run focused frontend tests, typecheck/build, focused Go target-replacement/preflight/media tests, and build the backend binary.
- Full-suite failures must be isolated by rerunning the exact changed scopes; report unrelated failures explicitly rather than treating them as evidence for or against this change.
- After deployment, verify the actual systemd listener from service logs/config, public hashed assets, and authenticated browser behavior before saying READY.
