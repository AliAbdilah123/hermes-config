# Browser video crop/trim processing triage

Use when Post Reels / video upload appears stuck at `Processing… N%` after the user applies trim/crop.

## Current flow

- The progress shown in `VideoCropModal.tsx` is **client-side** processing, before any backend upload.
- Frontend imports `@ffmpeg/ffmpeg` and `@ffmpeg/util`.
- `getFFmpeg()` loads FFmpeg WASM from `https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm`.
- `handleApply()` writes the selected file to FFmpeg's virtual FS, runs `ff.exec(args)`, reads `output.mp4`, then calls `onApply(outFile)`.
- Only after `onApply` do `CreatePostPage` / `EditPostPage` call `POST /api/posts/media`.
- Backend `UploadMedia` only parses and saves the multipart file; it does not crop/transcode video.

## Root-cause pattern

If UI is stuck/slow at `Processing… 8%` or similar, do not start in the backend publisher. First inspect the browser FFmpeg path:

```ts
await ff.writeFile("input.mp4", await fetchFile(file))
await ff.exec(args)
const data = await ff.readFile("output.mp4")
```

Cropping (`-vf crop=...`) forces video re-encode in browser WASM. Browser/WASM video re-encode is slow for normal reel-length video, screen recordings, variable-frame-rate sources, and high-bitrate uploads.

## Implemented fast-path pattern

SocialZen now centralizes FFmpeg args in:

- `apps/frontend/src/lib/video-processing.ts`
- Regression test: `apps/frontend/src/lib/video-processing.test.ts`

Expected command shapes:

```ts
// Trim only: fast input seek + stream copy, avoids re-encode.
["-ss", START, "-i", "input.mp4", "-t", DURATION, "-c", "copy", "-avoid_negative_ts", "make_zero", "output.mp4"]

// Crop + optional trim: still re-encodes, but uses input seek and ultrafast x264.
["-ss", START, "-i", "input.mp4", "-t", DURATION, "-vf", CROP, "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-c:a", "copy", "output.mp4"]
```

Keep this logic in the helper, not inline in `VideoCropModal.tsx`, so command-shape regressions stay testable without browser FFmpeg.

## Backend checks

- Verify service health, but expect no backend log during the stuck processing stage because the upload has not happened yet.
- Check `/api/posts/media` only after processing completes.
- Backend upload parse limit is currently `r.ParseMultipartForm(64 << 20)`. If FFmpeg output exceeds this, upload may fail after local processing with `BAD_UPLOAD`.

## Verification recipe

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm exec vitest run src/lib/video-processing.test.ts
pnpm typecheck
pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
curl -sI http://localhost/projects/socialzen/ | head -1
js=$(basename $(ls /var/www/html/projects/socialzen/assets/index-*.js | head -1))
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$js" | grep -i content-type
```

Expected: test pass, typecheck pass, build pass, local `HTTP/1.1 200 OK`, public JS `content-type: application/javascript`.

## Future upgrade path

If cropped exports are still too slow, do not keep micro-optimizing browser WASM. Move crop/trim to server-side/native FFmpeg or add a product-visible choice:

- **Fast export**: trim-only stream copy / upload original.
- **Exact crop export**: slower browser/server re-encode with progress and timeout messaging.
