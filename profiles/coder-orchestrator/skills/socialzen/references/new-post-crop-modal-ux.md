# New Post crop modal UX correction

When implementing SocialZen New Post image cropping, do **not** surface crop-ratio lists on the main New Post form. The main form should stay simple; ratio selection belongs only inside the crop/edit modal after the user selects media.

Expected crop modal shape:

- Header title should read `Crop Photo`.
- Large editor-style modal, not a small settings popover.
- Dark canvas/workspace with the image and visible crop handles.
- Right-side controls panel containing `ASPECT RATIO` buttons.
- Pressing a ratio button must immediately re-fit/adjust the crop box to that ratio.
- Include a bottom thumbnail strip with the current image selected.
- Include a `+` tile/button in the thumbnail strip so users can add another photo while still in the crop flow; new files should append to the crop queue instead of replacing the current pending crop.
- Top toolbar icons for tools like emoji/text/drawing can be placeholders for now; implementation can come later.

Implementation notes from the fixed session:

- `CreatePostPage.tsx` should compute requirements and pass `presets`/`defaultPreset` to `PhotoCropModal`, but should not render a main-page compatibility/ratio card unless specifically requested.
- If file selection happens while a crop modal already has `pendingFile`, append allowed files to `cropQueue` and keep the current crop modal active.
- Keep New Post ratios locked by passing `allowCustomRatio={false}`.
- Preserve the existing browser-canvas JPEG crop output and touch/pointer handling.
