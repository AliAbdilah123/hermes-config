Roots: SocialZen ~/socialzen; Paragentix ~/projects/paragentix; Komuna ~/projects/komuna; TemuBisnis ~/projects/temubisnis (Go/SQLite/React-Vite). Use project root; delegates request terminal; retry indirect failures directly.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
Public server endpoint is dev.ahsanworks.com. HTTP :80, HTTPS :443 (self-signed /etc/nginx/ssl/). Certbot installed. OCI Security List must allow new ports (cannot be done from terminal). See nginx-server-admin skill.
§
Migrations preserve/convert source identity in place or clone. Boilerplate is pattern-only unless requested.
§
PRD/docs HTML: deploy to /usr/share/nginx/html/prds/ (nginx /prd/ alias), set 644. Verify with curl -sI http://localhost/prd/name.
§
When implementing a new project, start from scratch — copy or use the boilerplate project as a clean slate unless the user explicitly specifies otherwise. Do not try to retrofit or evolve an existing unrelated project into the new one.
§
Komuna public site link is https://komuna.ahsanworks.com/ (root). Do not report /projects/komuna for Komuna final links unless explicitly verifying an nginx subpath artifact.
§
Discord #p-selfflow deploy path: https://selfflow.ahsanworks.com is served by nginx from /var/www/html/projects/self-flow behind Cloudflare cache; pushing git does not update live site. Build packages/fe, copy from a clean dist/ to that directory, and if cache-busting, rename/rewrite all JS chunks together before rsync.
§
Paragentix: default path ~/projects/paragentix. Inspect first and propose for explicit approval; approval moves job to todo for queue processing. After restarts revisit “session missing” jobs and sync status. Omit supplied “Done definition” from task prompts.
§
Paragentix public link is https://app-dev.paragentix.com.
§
Komuna Sessions: Admin attendance separate; answers stay in Attendant disclosure. Simple product defaults None; owned vouchers save without checkout. If none owned, show ≤3 packages default None; Buy preserves draft/returns to edit; Checkout and save persists after payment.