# Port sharing and frontend API path lessons
- When the UI is served via `/projects/<project>/`, fetch APIs through that same
  prefix: `/projects/<project>/api/v1/...`. A relative prefix like
  `./api/v1/...` avoids mismatch when base path changes.
- On Oracle Linux, do not create a second `server { listen 80; server_name _; }`
  block if one already exists. Merge new project locations into the existing
  default_server config (typically `/etc/nginx/conf.d/demo.conf`).
- If `nginx -t` reports `conflicting server_name "_"`, the new config created a
  duplicate server block. Remove the duplicate file and reload.
- Port 8080 is often occupied here. Use another local port (e.g. 9090) for the
  Go backend and update the proxy_pass target.
- File walking with naive `os.ReadDir` recursion returns cache/build files. Use
  `du` or `find ... -printf '%s %p\n'` for realistic disk hogs.
- Init CPU sampling from `/proc/stat` before starting the HTTP server so the
  first device request returns real delta CPU %.
