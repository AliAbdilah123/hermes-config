# Photo and carousel published-ratio consistency

## Trigger

Use when cropped images look correct in the crop editor or local preview but appear differently after Meta publishes them.

## Root cause pattern

Validating each image independently against the set of allowed feed ratios is insufficient for multi-image posts. A batch can pass while mixing `1:1`, `4:5`, and `1.91:1`. Meta may normalize the published post to the first image's ratio, so later items no longer match the editor preview.

## Minimal contract

1. Materialize the selected crop into the actual `File` that will be uploaded; never upload the original after Apply.
2. Validate the generated dimensions, not only crop UI state.
3. For multi-image Photo and Carousel batches, require every generated image to match the first generated image's ratio within proportional tolerance (about 1%).
4. Also require every item to match an allowed platform preset.
5. Validate the whole batch atomically before uploading any item. On mismatch, keep the editor open and select the first invalid image.
6. Preserve stable file order because the first item establishes the provider ratio.
7. Keep preview URLs, persisted `post_media.url`, and publisher inputs sourced from the same uploaded cropped file.

## Regression shape

Create two generated image records where the first is `1000x1000` and the second is `800x1000`. Both are individually valid presets, but batch validation with ratio locking must reject index 1. A same-ratio batch must pass without reordering.

## Verification

Run the focused crop test, TypeScript check, and a fresh production build. After deployment, verify the public hashed Create Post/Photo Crop asset returns `application/javascript`; source tests alone do not prove the deployed bundle is current.
