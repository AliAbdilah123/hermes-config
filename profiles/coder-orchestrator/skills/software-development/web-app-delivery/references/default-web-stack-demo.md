# Demo Nginx Config

## Default server block
```nginx
server {
  listen 80 default_server;
  server_name _;

  location /wiki/ {
    proxy_pass http://127.0.0.1:8080/api/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location /api/v1/ {
    proxy_pass http://127.0.0.1:8080/api/v1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location /projects/demo/ {
    alias /usr/share/nginx/html/projects/demo/;
    index index.html;
    try_files $uri $uri/ /projects/demo/index.html;
  }

  location / {
    root /usr/share/nginx/html;
    index index.html index.htm;
  }
}
```

## Deployment checklist
1. Ensure `nginx -t` passes.
2. Run `sudo nginx -s reload`.
3. Verify backend: `curl -I -s http://127.0.0.1:8080/api/v1/hello`.
4. Verify nginx API: `curl -I -s http://127.0.0.1/api/v1/hello`.
5. Verify frontend: `curl -I -s http://127.0.0.1/projects/demo/`.
6. Verify public: `curl -I -s http://<publicIP>/projects/demo/`.

## Observed failure modes
- `stat() ... Permission denied` on user home paths: nginx worker lacks read permission or SELinux blocks access. Fix by copying the build to `/usr/share/nginx/html/projects/<projectName>/` and `chown -R nginx:nginx`.
- `stat() ... dist/projects/demo/index.html`: `root` plus `try_files` appends the location prefix to the root. Use `alias` instead.
