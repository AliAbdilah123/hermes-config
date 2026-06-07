# Prefixed project 404: nginx backend proxy blocks missing

## Pattern
Some `/projects/<name>/` frontends render fine because nginx aliases their static assets, but calls to `/projects/<name>/api/v1/...` still 404.

## Likely cause
The nginx config lacks the `/projects/<name>/api/v1/ { proxy_pass http://127.0.0.1:<port>/api/v1/; }` block for that project, so requests never reach the backend.

## Fix sequence on this host
1. Find the backend authoritative path: `grep -Rni "127.0.0.1" /etc/nginx/projects/default.conf`.
2. Add the missing `location /projects/<name>/api/v1/` block.
3. Ensure the backend is running locally; proxy 502 not 404 means assets are up but backend is down or unreachable.
4. Reload nginx and re-test the prefixed API path.
