# Platform-aware image crop implementation

Use this when implementing New Post image crop rules after a reviewed plan is approved.

## Frontend shape

- Keep rules in one small module, e.g. `apps/frontend/src/lib/media-requirements.ts`.
- Model only the ratios the posting UI is allowed to expose:
  - Feed/photo/carousel: `1:1`, `4:5`, `1.91:1`.
  - Story image: `9:16`, default and only preset.
- `CreatePostPage.tsx` should compute requirements from `platforms` + `postType`, show allowed-ratio guidance near the Media upload zone, and pass `presets`, `defaultPreset`, and `allowCustomRatio={false}` to `PhotoCropModal` for image uploads.
- Preserve video flow; do not route videos through `PhotoCropModal`.
- Keep Instagram as the strictest cross-posting constraint. Facebook-only can still use the same Meta-safe presets for simplicity.
- Add a tiny helper test for the requirements module (`vitest` direct binary is fine).

## PhotoCropModal changes

- Extend existing `PhotoCropModal`; do not add a crop dependency.
- Add `9:16` preset support.
- Add optional locked presets prop and an `allowCustomRatio` prop.
- For New Post usage, hide `free` and custom W:H so resizing always preserves one selected valid ratio.
- Keep existing mobile gesture ownership and dark-mode handle exceptions intact.

## Backend safety net

- In `internal/posts/handler.go` upload path, use Go stdlib `image.DecodeConfig` for `image/*` uploads before saving.
- Import image decoders with blank imports (`image/jpeg`, `image/png`; `image/gif` only if accepting gif). Reset the multipart file to offset 0 before passing to `models.SaveUpload`.
- Return a stable API error code such as `INVALID_IMAGE` if DecodeConfig fails.
- Do not add server-side cropping in V1; browser canvas output is the product behavior.

## Verification/deploy checklist

```bash
cd apps/frontend
pnpm exec vitest run src/lib/media-requirements.test.ts
pnpm typecheck
pnpm build

cd ../backend-go
gofmt -w internal/posts/handler.go
go test ./internal/posts
go build -o /tmp/socialzen-api .
```

Deploy frontend and backend, then verify:

```bash
sudo systemctl restart socialzen.service
systemctl is-active socialzen.service
curl -sS -m 5 -i http://127.0.0.1:8089/health | head -5

js=$(basename $(ls /var/www/html/projects/socialzen/assets/CreatePostPage-*.js | head -1))
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$js" | grep -i content-type
grep -R "Crop ratios" -n /var/www/html/projects/socialzen/assets/CreatePostPage-*.js | head
```

Expected: service active, health `200 OK`, JS content type `application/javascript`, and deployed bundle contains the distinctive crop-ratio copy.
