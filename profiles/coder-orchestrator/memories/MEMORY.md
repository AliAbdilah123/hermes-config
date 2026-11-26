Social Notes supports Reels and ordered carousels. Webhooks store only original media URL+ID, never fetch media. Note Details lazily fetches/caches missing data, degrades gracefully, and retries later.
§
Default project URL: https://dev-{slug}.ahsanworks.com, mounted at `/` with no user-visible `/projects/...`, unless specified. Exceptions: selfflow.ahsanworks.com and shareexpense.ahsanworks.com, also root-mounted.
§
Non-project links (PRDs, docs, etc.) use https://dev.ahsanworks.com. PRD/docs files: /usr/share/nginx/html/prds/, mode 644.
§
New projects start from a clean boilerplate unless the user specifies otherwise; do not retrofit unrelated projects.
§
Discord #p-selfflow deploy path: https://selfflow.ahsanworks.com is served by nginx from /var/www/html/projects/self-flow behind Cloudflare cache; pushing git does not update live site. Build packages/fe, copy from a clean dist/ to that directory, and if cache-busting, rename/rewrite all JS chunks together before rsync.
§
Paragentix: ~/projects/paragentix; link https://app-dev.paragentix.com. Inspect first, propose for approval (moves job to todo). Revisit "session missing" jobs after restarts; omit "Done definition" from prompts.
§
Komuna Sessions: Admin attendance separate; answers stay in Attendant disclosure. Simple product defaults None; owned vouchers save without checkout. If none owned, show ≤3 packages default None; Buy preserves draft/returns to edit; Checkout and save persists after payment.
§
Light POS: backend owns/stores receipt OCR; frontend uses same-origin prefill. Prefer archive. Auxiliary forms use accessible modals except New Order. Menu details: long press + keyboard equivalent. Tables: multi-select, unavailable visible/disabled. Expenses: required line items, computed total, expandable rows.
§
SocialZen Project is a container for multiple independently scheduled posts and project-scoped batch AI image/video generation.
§
Discord project defaults unless stated otherwise: #p-sproutly-learning=Sproutly Learning; #p-general-agent=general-agent.
§
designs.ahsanworks.com = self-hosted OpenDesign (nginx basic-auth, :7461); repo /home/ubuntu/projects/open-design.