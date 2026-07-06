# Media upload progress for videos and carousels

Use when users report Reel/video/carousel upload feels stuck or they do not know how long it will take.

## Root cause pattern

`fetch()` uploads do not expose browser upload progress. If `/api/posts/media` is called through `apiRequest()`/`fetch()`, the UI can only show a spinner (`Uploading…`) even while a large MP4 or mixed carousel is actively transferring.

## Fix pattern

Add or reuse an XHR multipart helper for media uploads:

```ts
export function uploadFormData<T>(path: string, formData: FormData, onProgress: (percent: number) => void): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open("POST", apiUrl(path))
    xhr.withCredentials = true
    xhr.upload.onprogress = event => {
      if (event.lengthComputable) onProgress(Math.min(99, Math.round((event.loaded / event.total) * 100)))
    }
    xhr.onload = () => {
      const body = (xhr.responseText ? JSON.parse(xhr.responseText) : {}) as Record<string, unknown>
      if (xhr.status >= 200 && xhr.status < 300) {
        onProgress(100)
        resolve(body as T)
        return
      }
      reject(new ApiError(xhr.status, String(body.error ?? body.code ?? "UNKNOWN"), String(body.message ?? body.error ?? xhr.statusText), body))
    }
    xhr.onerror = () => reject(new ApiError(0, "NETWORK", "Network error", null))
    xhr.send(formData)
  })
}
```

Then use it in `CreatePostPage.tsx` and `EditPostPage.tsx` for `/api/posts/media`, passing item index and total count into state so carousel uploads show clear progress, e.g. `Uploading 2/3 · 64%` plus a progress bar.

## UX distinction

Keep browser FFmpeg processing separate from upload progress:

- `Processing… N%` = local video crop/trim/export in `VideoCropModal`.
- `Uploading item/total · N%` = actual multipart transfer to `/api/posts/media`.

For carousels, compute `item = existingUploaded.length + 1` and `total = existingUploaded.length + remaining.length + 1` at the moment each upload starts.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck
pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
curl -sI http://localhost/projects/socialzen/ | head -1
js=$(basename $(ls /var/www/html/projects/socialzen/assets/index-*.js | head -1))
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$js" | grep -i content-type
```

Expected: typecheck/build pass, local `HTTP/1.1 200 OK`, public JS `content-type: application/javascript`.
