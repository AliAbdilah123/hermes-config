# WhatsApp-style Video Trim/Crop Modal

Use when redesigning SocialZen's `VideoCropModal.tsx` or similar media editor UI.

## Pattern

- Keep the existing FFmpeg processing path (`buildVideoProcessArgs`, `@ffmpeg/ffmpeg`, `fetchFile`) unless the request explicitly changes export behavior.
- Make UI changes around the processing path rather than rewriting media handling.
- Put the trim timeline above the video preview for WhatsApp Status-like editing.
- Show concise metadata beside the timeline: total duration + file size (`0:36 • 1.6 MB`).
- Show live selected range and dynamic trim duration while dragging (`0:03 – 0:21 • Trim 0:18`).
- Remove manual crop-ratio selector from video editor UI; derive ratio from post context. For current SocialZen behavior: stories use `9:16`, normal video/reel posts can stay `free` unless platform rules require stricter cropping.
- Remove percentage/progress bars if the request asks for a lightweight editor; a small `Loading FFmpeg…` / `Processing…` text is enough.
- Add a Download action by reusing the same processing function as Apply, then generating an object URL and clicking a temporary `<a download>`.
- Use `rgb(254,254,254)` for intentional white handles/borders on black media surfaces so SocialZen's broad dark-mode fallback selectors do not recolor them.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck && pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
curl -sI http://localhost/projects/socialzen/ | head -1
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<changed-js>" | grep -i content-type
```

For Vite lazy chunks, the modal may bundle into a shared chunk such as `post-errors-*.js`, not necessarily `CreatePostPage-*.js`; grep all deployed JS assets for distinctive markers like `trimmed.mp4`, `Trim & Crop Video`, or `Loading FFmpeg`.
