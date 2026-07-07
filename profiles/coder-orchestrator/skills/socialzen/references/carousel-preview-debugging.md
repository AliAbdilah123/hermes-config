# Carousel preview debugging

When a user says a carousel still shows only one media item in Post Details/List preview:

1. First verify live persistence/API before changing upload code:
   ```bash
   sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT post_id, position, media_type, url FROM post_media WHERE post_id='<post_id>' ORDER BY position;"
   curl -sS -H 'Cookie: brand_session=<token>' 'http://127.0.0.1:8089/api/posts?limit=5' \
     | python3 -c 'import sys,json; j=json.load(sys.stdin); [print(p["id"], p["type"], len(p.get("media",[])), [m.get("mediaType") for m in p.get("media",[])]) for p in j["posts"]]'
   ```
2. If `post_media`/API returns multiple items, the bug is presentation or stale frontend assets — not upload persistence.
3. For mobile Post Details, tiny square thumbnails can still feel like “one media”. Prefer an obvious horizontal slide strip: `flex gap-2 overflow-x-auto snap-x`, up to 3 media items, with `1/N` badges and `+N` overlay for overflow.
4. After deploy, verify the production chunk contains the new UI marker/class, not just localhost build output:
   ```bash
   curl -s https://socialzen.ahsanworks.com/projects/socialzen/assets/PostsPage-<hash>.js | grep -o 'snap-mandatory\|min-w-\[31%\]'
   ```
5. If production is correct but user still sees old UI, ask for a hard refresh/close-reopen because browser/Cloudflare may hold the old frontend bundle.

Do not immediately rework backend persistence if the API already returns all carousel media.