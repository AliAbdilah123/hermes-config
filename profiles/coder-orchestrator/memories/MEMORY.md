#p-delegate=delegate; #p-boilerplate=boilerplate
§
SocialZen defaults to /home/ubuntu/socialzen, including jobs. Use direct terminal there; delegates explicitly request terminal and indirect failures retry directly. Frontend deploys to /var/www/html/projects/socialzen/; Cloudflare caches 4 hours.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
Public server endpoint is dev.ahsanworks.com. HTTP :80, HTTPS :443 (self-signed /etc/nginx/ssl/). Certbot installed. OCI Security List must allow new ports (cannot be done from terminal). See nginx-server-admin skill.
§
For migrations, don't recreate from boilerplate by default; port/convert the source project in place or into a clone, preserving identity. Use boilerplate only as a pattern reference unless user says otherwise.
§
PRD/docs HTML: deploy to /usr/share/nginx/html/prds/ (nginx /prd/ alias), set 644. Verify with curl -sI http://localhost/prd/name.
§
When implementing a new project, start from scratch — copy or use the boilerplate project as a clean slate unless the user explicitly specifies otherwise. Do not try to retrofit or evolve an existing unrelated project into the new one.
§
Komuna public site link is https://komuna.ahsanworks.com/ (root). Do not report /projects/komuna for Komuna final links unless explicitly verifying an nginx subpath artifact.
§
Discord #p-selfflow project public link: https://selfflow.ahsanworks.com (not /projects/self-flow/).
§
Discord #p-selfflow deploy path: https://selfflow.ahsanworks.com is served by nginx from /var/www/html/projects/self-flow behind Cloudflare cache; pushing git does not update live site. Build packages/fe, copy from a clean dist/ to that directory, and if cache-busting, rename/rewrite all JS chunks together before rsync.
§
Paragentix defaults to /home/ubuntu/projects/paragentix, including jobs. Use direct terminal there; delegates must explicitly request terminal; retry indirect failures directly. After restarts, revisit “session missing” jobs and sync status. Omit any supplied “Done definition” from task prompts.
§
Paragentix public link is https://app-dev.paragentix.com.