# Mobile carousel video picker MIME filtering

Use when SocialZen supports mixed image/video carousels in its publisher, but recorded phone videos are absent from the browser file picker.

## Diagnosis

Trace the full boundary before changing publishing code:

1. Confirm the provider publisher supports carousel video children and preserves each item’s media type.
2. Inspect the frontend `<input type="file">` `accept` value for the carousel post type.
3. Compare the picker filter with the ingestion logic. A common mismatch is:

```ts
CAROUSEL_ALBUM: "image/jpeg,image/png,video/mp4,video/quicktime"
```

while `handleFiles` and the backend accept `file.type.startsWith("video/")` / `Content-Type: video/*`.

Phone recordings may be exposed as `video/3gpp`, `video/webm`, or another device/browser-specific video MIME type. An explicit MP4/QuickTime allowlist can therefore hide otherwise acceptable recordings before application validation runs.

## Minimal fix

When downstream validation genuinely accepts generic video input, align the picker with it:

```ts
CAROUSEL_ALBUM: "image/jpeg,image/png,video/*"
```

Keep the explicit image allowlist if only JPEG/PNG are supported. Do not add `capture`, because that can force camera capture instead of allowing users to browse existing recordings.

## Verification

- Add a focused test for the carousel `accept` contract or export a small helper/constant for testing.
- Verify existing carousel handling still accepts both images and videos.
- Run frontend typecheck, focused tests, and production build.
- On a real mobile browser, select Threads → Carousel and confirm an existing camera-recorded video appears in the chooser and reaches upload.
- Treat file visibility, successful upload, and provider publication as separate gates; source inspection alone does not prove mobile-picker behavior.
