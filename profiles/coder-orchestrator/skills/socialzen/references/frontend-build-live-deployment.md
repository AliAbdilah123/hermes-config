# SocialZen frontend build → live deployment

A successful Vite build and API service restart do not publish frontend changes. Nginx serves SocialZen from `/var/www/html/projects/socialzen/`, while the repository build lands in `apps/frontend/dist/`.

## Required sequence after every feature or bugfix

From the SocialZen repository:

```bash
cd apps/frontend
npm run typecheck
npm test -- --run <focused-test-file>
npm run build
cd ../..
sudo rsync -a --delete apps/frontend/dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
sudo systemctl restart socialzen.service
sudo systemctl is-active socialzen.service
```

Use `rsync --delete` only from a fresh successful `dist/` build. It prevents stale hashed chunks from accumulating.

## Verification: prove the new UI is actually served

Do not treat service-active or HTTP 200 as frontend deployment proof. Fetch the public HTML, resolve its current hashed entry bundle and lazy page chunk, then assert stable markers from the implemented UI exist in that served chunk.

Example pattern:

```bash
curl -fsS 'https://dev-socialzen.ahsanworks.com/app/projects?deploy=<commit>' -o /tmp/socialzen-live.html
# Extract the current index-*.js from HTML, fetch it, then extract/fetch the relevant lazy chunk.
# Assert durable strings/classes unique to the feature are present.
curl -sS -o /dev/null -w '%{http_code}\n' 'https://dev-socialzen.ahsanworks.com/app/projects?deploy=<commit>'
sudo systemctl is-active socialzen.service
```

Also compare the live HTML asset hashes with `apps/frontend/dist/index.html`. If they differ, nginx is still serving an older build.

## Common pitfall

`sudo systemctl restart socialzen.service` restarts only the Go API at `/opt/socialzen/socialzen-server`. It does not copy frontend assets. A report that says “restarted and HTTP 200” is incomplete unless the live hashed frontend asset contains the new implementation marker.
