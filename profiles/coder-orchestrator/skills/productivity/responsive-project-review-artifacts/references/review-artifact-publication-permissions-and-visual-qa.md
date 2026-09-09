# Review artifact publication permissions and visual QA

## Nginx publication fallback

A symlink under `/usr/share/nginx/html/prds/` can return `403 Forbidden` even when the source file is mode `0644`, because the nginx worker may not be allowed to traverse a source parent directory such as a home-directory worktree.

1. Use the normal canonical-doc symlink only when its parent path is nginx-traversable.
2. Verify the exact local and public URLs immediately; `nginx -t` proves configuration syntax, not artifact readability.
3. If either URL returns 403, remove only that artifact symlink and copy the HTML into `/usr/share/nginx/html/prds/<slug>.html` with mode `0644`.
4. After each revision, copy again and verify the cache-busted public body contains a distinctive updated phrase or CSS token, not merely HTTP 200.

Do not broaden home/worktree directory permissions just to make one artifact symlink work.

## Rendered visual QA

HTTP verification is transport proof only. For design-heavy review pages:

- Render desktop and 390px mobile screenshots with browser tooling or installed headless Chromium.
- Check overlap, clipping, horizontal overflow, contrast, and selector wrapping.
- Treat 10px metadata/eyebrow text as suspect on mobile; use about 12px unless the rendered result clearly remains legible.
- Fix visible issues, republish, then verify a cache-busted response contains the revised CSS/content.
- If one browser wrapper times out but headless Chromium works, use the successful rendered evidence; preserve the fallback pattern rather than a permanent negative claim about the tool.
