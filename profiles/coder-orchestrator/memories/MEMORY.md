#p-delegate=delegate; #p-boilerplate=boilerplate
§
WorkingDirectory /opt/socialzen. Frontend dist deploys to /var/www/html/projects/socialzen/ (nginx alias), NOT /var/www/socialzen/. Cloudflare fronts socialzen.ahsanworks.com with 4-hour cache.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
Public host IP 168.110.213.104. HTTP :80, HTTPS :443 (self-signed /etc/nginx/ssl/). Certbot installed. OCI Security List must allow new ports (cannot be done from terminal). See nginx-server-admin skill.
§
For migrations, don't recreate from boilerplate by default; port/convert the source project in place or into a clone, preserving identity. Use boilerplate only as a pattern reference unless user says otherwise.
§
PRD/docs HTML: deploy to /usr/share/nginx/html/prds/ (nginx /prd/ alias), set 644. Verify with curl -sI http://localhost/prd/name.
§
When implementing a new project, start from scratch — copy or use the boilerplate project as a clean slate unless the user explicitly specifies otherwise. Do not try to retrofit or evolve an existing unrelated project into the new one.
§
Discord project defaults: #p-komuna=Komuna at /home/ubuntu/projects/komuna/; #p-socialzen=/home/ubuntu/socialzen/; #p-share-expense=shareexpense.ahsanworks.com. Use channel/thread as primary signal; verify and load matching project skill before project work. Komuna subscription model: Package sells; Voucher redeems; SubscriptionEntitlement is renewable one-product access; VoucherClaim records usage; multi-product bundles grant multiple entitlements; cancel/manage in Wallet.
§
Discord #p-selfflow project public link: https://selfflow.ahsanworks.com (not /projects/self-flow/).
§
Discord #p-selfflow deploy path: https://selfflow.ahsanworks.com is served by nginx from /var/www/html/projects/self-flow behind Cloudflare cache; pushing git does not update live site. Build packages/fe, copy from a clean dist/ to that directory, and if cache-busting, rename/rewrite all JS chunks together before rsync.