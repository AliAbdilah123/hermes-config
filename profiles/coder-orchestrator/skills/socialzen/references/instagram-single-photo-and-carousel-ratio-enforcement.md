# Instagram single-photo and carousel ratio enforcement

## Trigger

Use when Instagram PHOTO accepts several images, users need guidance toward Carousel, or untouched carousel items fail with `Photo N does not match an allowed aspect ratio.`

## Root causes

1. The composer can share one generic multi-image limit between PHOTO and CAROUSEL, allowing an invalid Instagram PHOTO payload.
2. Backend publishing may preserve legacy multi-photo behavior, so a frontend-only restriction is bypassable.
3. In batch cropping, only the active image has stored crop state. Untouched images fall back to a normalized full-frame box (`0,0,1,1`); materializing that box preserves each source ratio, then batch ratio validation rejects later items even though the selected preset should apply to the batch.

## Minimal contract

- For any post targeting Instagram, PHOTO accepts exactly one image.
- Keep CAROUSEL_ALBUM at up to 10 items and tell users to use Carousel for multiple photos.
- Enforce the PHOTO limit in both the file picker/composer and `CreatePost`; return a stable API code such as `INSTAGRAM_PHOTO_SINGLE_MEDIA`.
- Do not remove Facebook's supported multi-photo PHOTO behavior: derive the limit from selected platforms.
- For a carousel batch, untouched files inherit the currently selected batch preset. Before canvas materialization, convert their full-frame fallback into a centered crop box fitted to that preset ratio.
- Preserve explicit per-file crop memory and stable file order; only synthesize the fitted box for untouched full-frame fallback state.
- Validate all generated dimensions atomically against allowed presets and the first item's ratio before uploading anything.

## Regression checks

Frontend:
- Instagram PHOTO limit is 1; CAROUSEL_ALBUM limit is 10.
- A portrait and landscape source both produce a centered square box when the selected batch ratio is 1:1.
- Existing batch validation still rejects genuinely mismatched generated ratios.

Backend:
- Creating an Instagram PHOTO with two media items returns HTTP 400 and `INSTAGRAM_PHOTO_SINGLE_MEDIA`.
- Existing multi-account target creation remains valid for one-media PHOTO payloads.

## Verification

Run the focused crop/media-limit tests, TypeScript check, and production frontend build. Run targeted CreatePost tests and a Go build. After deployment, verify the public CreatePost asset is JavaScript and contains the one-photo/Carousel guidance marker.
