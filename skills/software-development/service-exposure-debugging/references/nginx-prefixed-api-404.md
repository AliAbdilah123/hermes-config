# Path-prefixed frontends rendering but backend APIs 404

## Pattern
Static assets render from `/projects/<name>/` but browser network tab shows 404 for `/projects/<name>/api/v1/...`.

## Root cause class
Three things can each produce this symptom:
1. The backend is not running.
2. The backend is running and reachable on 127.0.0.1, but nginx is missing the per-project `location /projects/<name>/api/v1/ { proxy_pass ...; }` proxy block.
3. The backend only accepts requests on the public IP and the frontend uses a base path that does not reach it.

## Fix sequence
1. Verify backend is listening locally: `curl http://127.0.0.1:<port>/api/v1/<test>`.
2. If 404 on 127.0.0.1, check the backend’s actual registered routes; 404 means path mismatch inside the backend.
3. If backend responds, but the public path still 404s, add or fix the proxy block in nginx with the same trailing slash pattern on both sides: `/projects/<name>/api/v1/` -> `http://127.0.0.1:<port>/api/v1/`.
4. Reload nginx, then test end-to-end from the prefixed URL.

## Diff hint
Missing block to add:
```nginx
location /projects/<name>/api/v1/ {
    proxy_pass http://127.0.0.1:<port>/api/v1/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
