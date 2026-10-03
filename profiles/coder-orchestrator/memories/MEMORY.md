Roots: SocialZen ~/socialzen; Paragentix ~/projects/paragentix; Komuna ~/projects/komuna; TemuBisnis ~/projects/temubisnis; Light POS ~/projects/light-pos; Social Notes ~/projects/social-media-note-taking-app. Social Notes supports Instagram Reels and ordered carousel media.
§
Default project URL: https://dev-{slug}.ahsanworks.com unless specified. Exceptions: selfflow.ahsanworks.com, shareexpense.ahsanworks.com.
§
PRD/docs HTML: deploy to /usr/share/nginx/html/prds/ (nginx /prd/ alias), set 644. Verify with curl -sI http://localhost/prd/name.
§
New projects start from a clean boilerplate unless the user specifies otherwise; do not retrofit unrelated projects.
§
Discord #p-selfflow deploy path: https://selfflow.ahsanworks.com is served by nginx from /var/www/html/projects/self-flow behind Cloudflare cache; pushing git does not update live site. Build packages/fe, copy from a clean dist/ to that directory, and if cache-busting, rename/rewrite all JS chunks together before rsync.
§
Paragentix: default path ~/projects/paragentix. Inspect first and propose for explicit approval; approval moves job to todo for queue processing. After restarts revisit “session missing” jobs and sync status. Omit supplied “Done definition” from task prompts.
§
Paragentix public link is https://app-dev.paragentix.com.
§
Komuna Sessions: Admin attendance separate; answers stay in Attendant disclosure. Simple product defaults None; owned vouchers save without checkout. If none owned, show ≤3 packages default None; Buy preserves draft/returns to edit; Checkout and save persists after payment.
§
Light POS: backend owns/stores receipt OCR; frontend uses same-origin prefill. Prefer archive. Auxiliary forms use accessible modals except New Order. Menu details: long press + keyboard equivalent. Tables: multi-select, unavailable visible/disabled. Expenses: required line items, computed total, expandable rows.
§
SocialZen Project is a container for multiple independently scheduled posts and project-scoped batch AI image/video generation.