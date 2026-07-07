# Instagram mixed carousel container `status=ERROR`

## Symptom

A carousel post with multiple images plus a video (for example 2 photos + 1 MP4) fails after publish with:

- parent post error: `All platforms failed to publish`
- target error: `Instagram container <id>: status=ERROR`

The app may have correctly persisted all media items in `post_media`; do not assume this is the older "only first carousel item saved" bug.

## Fast triage

1. Check the failed post and target error:
   ```bash
   sudo sqlite3 /opt/socialzen/data/socialzen.db "
   SELECT p.id,p.type,p.status,p.media_thumbnail,p.error_message,
     GROUP_CONCAT(pt.platform||':'||pt.status||':'||COALESCE(pt.error_message,''),' | ') targets
   FROM posts p LEFT JOIN post_targets pt ON pt.post_id=p.id
   WHERE p.status='FAILED'
   GROUP BY p.id ORDER BY p.updated_at DESC LIMIT 5;"
   ```
2. Confirm all carousel media rows exist and are ordered:
   ```bash
   sudo sqlite3 /opt/socialzen/data/socialzen.db "
   SELECT id,url,thumbnail_url,media_type,position
   FROM post_media WHERE post_id='<post_id>' ORDER BY position;"
   ```
3. Verify each public media URL is fetchable with the right content type and byte ranges:
   ```bash
   curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/media/...jpg"
   curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/media/...mp4"
   ```
   Expected for video: `content-type: video/mp4`, `accept-ranges: bytes`, realistic `content-length`.
4. Inspect the local MP4 if needed:
   ```bash
   ffprobe -v error -show_entries format=duration,size,format_name:stream=codec_type,codec_name,width,height,r_frame_rate -of default=nw=1 /opt/socialzen/data/media/<user>/<file>.mp4
   ```

## Interpretation

If `post_media` contains every item and the public URLs are valid, the failure is likely in Meta's processing of the mixed carousel container/children, not the upload UI or media persistence.

Current publisher behavior may only return `status=ERROR`, which is too opaque for a user-facing/debuggable failure. Improve polling to log/surface the full Graph response body/status fields before changing unrelated upload code.

## Fix direction

- Add/keep tests for Instagram form generation covering:
  - image carousel child: `is_carousel_item=true` + `image_url`
  - video carousel child: `is_carousel_item=true` + `media_type=VIDEO` + `video_url`
  - parent carousel: `media_type=CAROUSEL` + comma-separated `children`
- In `waitForInstagramContainer`, include the response body and any status fields Meta returns when status is `ERROR`/`EXPIRED` or timeout occurs.
- Only revisit media transcoding/format after proving Meta rejected a valid-looking MP4 and URLs are accessible.

## Pitfall

Do not collapse this into the older `media_thumbnail` bug. A post can have all three `post_media` rows and still fail because Meta marks the mixed carousel container as `ERROR` during processing.