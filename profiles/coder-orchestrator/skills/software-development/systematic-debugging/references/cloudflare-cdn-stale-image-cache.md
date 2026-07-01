# Cloudflare CDN Stale Image Cache Triage

## Symptoms
- Image previews broken in deployed SPA (blank/broken thumbnail icon)
- Origin serves the image correctly (`Content-Type: image/jpeg`)
- Public CDN URL returns `content-type: text/html` with `cf-cache-status: HIT`
- Fresh uploads work (new unique URLs), only older requests are affected

## Root Cause
The nginx config was missing the proxy location for the media/image path when the URL was first requested. The SPA fallback HTML (or nginx error page) got cached by Cloudflare with the image URL as the cache key, with a high `max-age` (typically 14400s / 4 hours for HTML fallbacks).

## Triage Commands

```bash
# 1. Verify origin serves correctly
curl -sI --max-time 5 http://127.0.0.1:<PORT>/media/<path> | grep -E 'Content-Type|Cache-Control'
# Expected: Content-Type: image/jpeg, Cache-Control: public, max-age=31536000, immutable

# 2. Check public CDN URL for stale cache
curl -sI --max-time 5 'https://<domain>/<path>/media/<file>' | grep -E 'content-type|cf-cache-status|cache-control'
# Stale: content-type: text/html, cf-cache-status: HIT, cache-control: max-age=14400
# Fresh: content-type: image/jpeg, cf-cache-status: MISS or EXPIRED

# 3. Cache-busted URL should bypass stale cache
curl -sI --max-time 5 'https://<domain>/<path>/media/<file>?v=<timestamp>' | grep -E 'content-type|cf-cache-status'
# Expected: content-type: image/jpeg, cf-cache-status: MISS
```

## Fix Pattern

### 1. Origin: Add Cache-Control headers in media handler
```go
// Go handler example
w.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
w.Header().Set("Content-Type", mimeType)
// Serve file...
```

### 2. API: Append cache-buster to response URLs
```go
// In the API handler that returns media URLs to the frontend:
if thumbnail != "" {
    thumbnail = thumbnail + "?v=" + strings.ReplaceAll(updatedAt, ":", "")
}
```
This ensures the frontend always requests URLs that bypass Cloudflare's stale cache entries.

### 3. Nginx: Add Cache-Control header on proxy location
```nginx
location ^~ /projects/<app>/media/ {
    proxy_pass http://127.0.0.1:<PORT>/media/;
    # ... standard proxy headers ...
    add_header Cache-Control "public, max-age=86400" always;
}
```

## Verification
After deploying the fix:
1. Origin returns correct `Content-Type` with `Cache-Control: immutable`
2. Cache-busted public URL returns `content-type: image/jpeg` with `cf-cache-status: MISS`
3. Fresh uploads work immediately (new unique file names)
4. Stale entries expire from Cloudflare after their remaining TTL (~2-4 hours after the nginx config was fixed)

## Key Insight
The `cf-cache-status: HIT` header is the definitive signal. MISS or EXPIRED means Cloudflare re-fetched from origin and got the correct response. HIT with `text/html` means the stale HTML is still cached.
