# Cloudflare Stale Cache After Nginx Routing Fix

## Symptom

You fixed an nginx routing config (added a missing location block, fixed a proxy, etc.) and verified it works when hitting the origin directly. But the public URL — going through Cloudflare — still returns the OLD bad response (e.g., HTML instead of an image, wrong content-type), even after `nginx -s reload`.

Checking response headers shows:
```
content-type: text/html        ← wrong, should be image/jpeg
cf-cache-status: HIT           ← Cloudflare is serving cached, not from origin
age: 6866                      ← cached ~2 hours ago
```

## Root Cause

Cloudflare proxied DNS caches responses from the origin server. Before the nginx fix, a request to the affected URL path returned a "wrong" response (e.g., HTML SPA fallback) with a valid HTTP 200. Cloudflare cached it with whatever `Cache-Control: max-age` the origin sent (typically 14400 = 4 hours from nginx defaults). After you fix the nginx config, Cloudflare still serves the cached version until it expires.

This is especially insidious for image/media URLs: the broken response is 200 HTML (not 404), so Cloudflare sees a "valid" response to cache.

## Investigation

1. **Test origin directly (bypass Cloudflare):**
   ```bash
   curl -sI http://168.110.213.104/projects/<slug>/media/<path>
   ```
   If this returns correct content-type → nginx fix is working, Cloudflare cache is the problem.

2. **Test public with cache-buster:**
   ```bash
   curl -sI "https://<domain>/projects/<slug>/media/<path>?v=$(date +%s)"
   ```
   If this returns correct content-type with `cf-cache-status: MISS` → confirmed: stale Cloudflare cache.

3. **Test public without cache-buster:**
   ```bash
   curl -sI https://<domain>/projects/<slug>/media/<path>
   ```
   If this returns wrong content-type with `cf-cache-status: HIT` → confirmed.

## Fix Options

### Option 1: Wait (fastest to deploy, slowest to resolve)
Cloudflare cache entries expire naturally (typically 4-hour max-age). Just wait. Downside: user sees broken images for hours.

### Option 2: Purge Cloudflare cache
Requires Cloudflare API credentials (Zone ID + API token). Run from any machine with curl:
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/purge_cache" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"files":["https://<domain>/projects/<slug>/media/<path>"]}'
```

### Option 3: Cache-busting in API responses (recommended permanent fix)
Append a unique query parameter to media URLs in the backend API response. Since media filenames are content-addressed (unique per upload), using `?v=<updatedAt>` ensures every post gets a fresh Cloudflare cache entry on the next API call.

Go example (in the FetchPosts/dashboard handler):
```go
thumbnail := models.Nullable(thumb)
if th, ok := thumbnail.(string); ok && th != "" {
    thumbnail = th + "?v=" + strings.ReplaceAll(updated, ":", "")
}
```

This is self-healing: as soon as the frontend fetches fresh API data, the new cache-busted URLs bypass the stale Cloudflare cache.

### Option 4: Add Cache-Control headers at nginx
Add to the location block so future cached responses get proper headers:
```nginx
location ^~ /projects/<slug>/media/ {
    proxy_pass http://127.0.0.1:<port>/media/;
    # ... other proxy settings ...
    add_header Cache-Control "public, max-age=86400" always;
}
```

This prevents NEW stale entries but doesn't fix already-cached ones. Combine with Option 3.

## Verification

```bash
# Origin (should be correct)
curl -sI http://168.110.213.104/projects/<slug>/media/<path> | grep -E 'Content-Type|Cache-Control'

# Public cache-busted (should be correct, MISS)
curl -sI "https://<domain>/projects/<slug>/media/<path>?v=<any>" | grep -E 'content-type|cf-cache-status'

# After fix: backend API response should have cache-busted URLs
curl -s -b 'brand_session=<token>' http://127.0.0.1:<port>/api/posts | \
  python3 -c "import json,sys; [print(p['mediaThumbnail']) for p in json.load(sys.stdin)['posts'] if p.get('mediaThumbnail')]"
# Should show URLs like: /projects/<slug>/media/user_xxx/upload_xxx.jpg?v=2026-07-01T045640Z
```

## Prevention

- Always include the path-prefixed media/api proxy blocks in BOTH the default config AND the domain config. See nginx-server-admin pitfall "Domain config missing path-prefixed media/api blocks".
- Add `Cache-Control: public, max-age=86400` header on media proxy locations in nginx.
- Add immutable `Cache-Control` in the Go backend's media handler.
- Consider using unique, content-addressed media filenames (e.g., upload hash) so each upload gets a fresh URL that can never conflict with a stale cache entry.
