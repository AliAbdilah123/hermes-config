# Komuna frontend deploy root

When deploying frontend-only Komuna web changes:

- Build from `/home/ubuntu/projects/komuna/apps/web` with `npm run build`.
- Deploy the SPA build with:

```bash
rsync -a apps/web/dist/ /var/www/html/projects/komuna/
```

- Verify the public host with:

```bash
curl -sI https://komuna.ahsanworks.com/ | head -n 5
```

## Pitfall

Do **not** rsync Komuna builds into `/usr/share/nginx/html/`, and do **not** use `--delete` against that shared web root. `/usr/share/nginx/html/prds/` is for PRD/review artifacts; the live Komuna SPA nginx root is `/var/www/html/projects/komuna/`.

If an accidental `rsync --delete` against `/usr/share/nginx/html/` reports permission-denied deletes for other projects/PRDs, stop and redeploy only to `/var/www/html/projects/komuna/` without `--delete`.
