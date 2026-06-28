# Vite + FFmpeg.wasm browser export deployment

Use this when a Vite/React SPA uses `@ffmpeg/ffmpeg` for browser-only video/audio rendering and export fails vaguely in production.

## Root cause pattern

FFmpeg.wasm commonly needs:
- FFmpeg core JS/WASM assets reachable under the deployed app base path.
- Browser isolation headers so `SharedArrayBuffer` can be used.
- Useful error surfacing instead of a generic `Export failed` message.

When the app is deployed under a subpath such as `/projects/<slug>/`, CDN or root-relative core URLs can be brittle. Prefer shipping `@ffmpeg/core` assets with the app and loading them from `import.meta.env.BASE_URL`.

## Implementation pattern

1. Install the matching core package:

```bash
npm install @ffmpeg/core@<version-compatible-with-@ffmpeg/ffmpeg>
```

2. Copy runtime assets into Vite public files so they deploy with the app:

```bash
mkdir -p public/ffmpeg
cp node_modules/@ffmpeg/core/dist/esm/ffmpeg-core.js \\
   node_modules/@ffmpeg/core/dist/esm/ffmpeg-core.wasm \\
   public/ffmpeg/
```

Use the **ESM** core JS with `@ffmpeg/ffmpeg`'s module worker. If you copy the UMD core, the worker can throw `failed to import ffmpeg-core.js` because the module-worker fallback expects a default export.

3. Load core assets from the deployed Vite base path:

```ts
const ffmpegCoreRevision = 'esm-YYYYMMDD-N'
const coreBaseURL = `${import.meta.env.BASE_URL}ffmpeg`
await ffmpeg.load({
  coreURL: `${coreBaseURL}/ffmpeg-core.js?v=${ffmpegCoreRevision}`,
  wasmURL: `${coreBaseURL}/ffmpeg-core.wasm?v=${ffmpegCoreRevision}`,
})
```

Add a revision query whenever switching core builds so browsers do not keep using a stale cached UMD core.

4. Add route-specific nginx headers for the app path:

```nginx
location /projects/video-slicer-editor/ {
    alias /var/www/html/projects/video-slicer-editor/;
    index index.html;
    add_header Cross-Origin-Opener-Policy same-origin always;
    add_header Cross-Origin-Embedder-Policy require-corp always;
    add_header Cross-Origin-Resource-Policy same-origin always;
    try_files $uri $uri/ /projects/video-slicer-editor/index.html;
}
```

5. Improve app-facing errors:

```ts
export function explainExportError(error: unknown): string {
  const rawMessage = error instanceof Error ? error.message : String(error || '')
  const message = rawMessage.toLowerCase()
  if (message.includes('sharedarraybuffer') || message.includes('cross-origin') || message.includes('crossoriginisolated')) {
    return 'Export needs browser isolation headers for FFmpeg. Refresh the page and try again; if it still fails, the deployment headers are missing.'
  }
  if (message.includes('failed to fetch') || message.includes('networkerror')) {
    return 'Export could not load the local FFmpeg runtime. Check the connection and refresh the page.'
  }
  if (rawMessage.trim()) return `Export failed: ${rawMessage}`
  return 'Export failed. Try a shorter clip or refresh the page before exporting again.'
}
```

## Verification

After build/deploy:

```bash
curl -sI http://<host>/projects/<slug>/ | grep -Ei 'Cross-Origin|HTTP/'
curl -s -o /tmp/ffmpeg-core.js -w '%{http_code}' http://<host>/projects/<slug>/ffmpeg/ffmpeg-core.js
curl -s -o /tmp/ffmpeg-core.wasm -w '%{http_code}' http://<host>/projects/<slug>/ffmpeg/ffmpeg-core.wasm
```

Expected:
- App returns `200`.
- Both FFmpeg core files return `200`.
- Headers include `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`.

## UI pitfall

For editor workflows, keep source video metadata out of the main clipping workspace. Put file metadata directly below the preview in a closed-by-default accordion/details element so clip controls remain visually dominant.
