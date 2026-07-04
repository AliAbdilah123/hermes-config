# Reel upload size limits

## Symptom

Instagram Reel upload fails after selecting a video, and still fails after using the crop modal. The UI may only show a generic upload failure.

## Root cause pattern

Browser-side FFmpeg cropping/re-encoding can produce an MP4 larger than the original or larger than 64 MiB. SocialZen's frontend advertises a 100 MB video limit, so every upload boundary must allow at least that much plus multipart overhead:

- Go upload handler: `r.ParseMultipartForm(...)`
- Nginx domain/server block: `client_max_body_size`
- Frontend error mapping: `ApiError.code`, because backend JSON is `{ error, code, message }`, not `{ error: { code } }`

If these are misaligned, a valid Reel under the UI limit can fail before publishing reaches Instagram.

## Fix checklist

1. In `apps/backend-go/internal/posts/handler.go`, keep `UploadMedia` multipart limit above 100 MB, e.g. `128 << 20`.
2. Return a concrete code for oversized multipart uploads:
   ```go
   models.WriteJSON(w, 400, models.ApiError{Error: "FILE_TOO_LARGE", Code: "FILE_TOO_LARGE"})
   ```
3. In create/edit post pages, map upload failures from `err.code` through `uploadErrorMessage(err.code)`.
4. In `/etc/nginx/projects/socialzen-domain.conf`, set `client_max_body_size 128m;` in the `socialzen.ahsanworks.com` server block.
5. Reload nginx and redeploy backend/frontend.

## Verification

- `go build -o /tmp/socialzen-api .` from `apps/backend-go`
- `pnpm build` from `apps/frontend`
- Upload a representative >64 MB MP4 against the deployed local API with an authenticated cookie and expect `201`:
  ```bash
  curl -s -o /tmp/upload-test.json -w '%{http_code}\n' \
    -b 'brand_session=demo-session' \
    -F 'file=@/tmp/reel-70mb.mp4;type=video/mp4' \
    -F 'purpose=REEL' \
    http://127.0.0.1:8089/api/posts/media
  ```
- Clean up any test media DB row/file afterward.
